from dbentities import Hashtag, Media, Url, UserMention
from dbentities import Base, Tweet, Timeline, User

from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.api import Twitter, TwitterError, TwitterHTTPError
from sqlalchemy.orm import sessionmaker
import json

CONSUMER_KEY = 'uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET = 'MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

API_VERSION = "1.1"
API_DOMAIN = "api.twitter.com"

USER_LIMIT = 100
TWEET_LIMIT = 200

# These are per hour in the 1.1 API
USER_TIMELINE_RATE_LIMIT = 180
USER_LOOKUP_RATE_LIMIT = 180


def do_oauth_dance(oauth_filename, key, secret):
    """
    Prompts user to create OAuth token and token secret
    and then saves them in filename
    """
    print(('OAuth file {} not found'.format(oauth_filename)))
    request = 'Do you want to initiate a new oauth dance (y or n)? '
    response = raw_input(request)
    if len(response) > 0 and response[0].upper() == 'Y':
        token, token_secret = oauth_dance('Eye spy you!',
                                            key,
                                            secret,
                                            oauth_filename)
    else:
        token = token_secret = ''
    return token, token_secret

def create_oauth(oauthfile, consumer_key, consumer_secret):
    """
    Creates and OAuth object using the tokens from the oauthfile and
    the consumer_key and consumer_secret. If the file doesn't exists
    we prompt the user to initiate the oauth dance, and save the
    token and token secret in the oauthfile
    """
    try:
        token, token_secret = read_token_file(oauthfile)
    except IOError:
        token, token_secret = do_oauth_dance(oauthfile, consumer_key,
                                                         consumer_secret)

    return OAuth(token, token_secret, consumer_key, consumer_secret)

def create_twitter(twitter_oauth, api_version=API_VERSION,
                        api_domain=API_DOMAIN, secure=True):
    """
    Creates and returns a Twitter API object
    """
    return Twitter(auth=twitter_oauth, secure=secure, api_version=api_version,
                    domain=api_domain)

def create_timeline_json(twitter_api, screen_name, tweet_count,
        since_id, max_id, include_rts, exclude_replies):
    """
    Gets json object from Twitter and returns it to the caller
    """
    # This needs to be the first statement so all the args/values are captured
    kwargs = locals()
    if not kwargs['since_id']:
        del kwargs['since_id']

    if not kwargs['max_id']:
        del kwargs['max_id']

    return twitter_api.statuses.user_timeline(**kwargs)

def create_tweet(tweet_json):
    """ Creates a Tweet object """
    tweet = Tweet(tweet_json['created_at'],
                    tweet_json['favorited'],
                    tweet_json['favorite_count'],
                    tweet_json['in_reply_to_screen_name'],
                    tweet_json['in_reply_to_status_id'],
                    tweet_json['in_reply_to_status_id_str'],
                    tweet_json['in_reply_to_user_id'],
                    tweet_json['in_reply_to_user_id_str'],
                    tweet_json['lang'],
                    tweet_json['retweet_count'],
                    tweet_json['retweeted'],
                    tweet_json['source'],
                    tweet_json['text'],
                    tweet_json['truncated'],
                    tweet_json['id'],
                    tweet_json['id_str'],
                    tweet_json['user']['id'])
    return tweet

def create_hashtags(hashtag_json, tweet_id):
    """Creates a list of Hashtag objects"""
    return [Hashtag(h['text'], tweet_id) for h in hashtag_json]

def create_urls(url_json, tweet_id):
    """Creates a list of Url objects"""
    return [Url(u['display_url'], u['expanded_url'], tweet_id, u['url'])
            for u in url_json]

def create_user_mentions(user_mentions_json, tweet_id):
    """Creates a list of Url objects"""
    return [UserMention(tweet_id, m['id']) for m in user_mentions_json]

def create_media(media_json, tweet_id):
    """Creates a list of Media objects"""
    return [Media(m['display_url'],
                    m['expanded_url'],
                    m['id'],
                    m['id_str'],
                    m['type'],
                    m['media_url'],
                    m['media_url_https'],
                    m['source_status_id'],
                    tweet_id,
                    m['url'])
            for m in media_json]

def create_timeline_pyobjs(timeline_json):
    """
    Transforms the json into dictionary of lists of Python objects for each
    object discovered
    """
    pyobjs = {'tweets': [],
              'hashtags': [],
              'media': [],
              'urls': [],
              'user_mentions': []}

    for t in timeline_json:
        tweet = create_tweet(t)
        tweet_id = tweet.tweet_id
        user_id = tweet.user_id
        ent = t['entities']
        hashtags = create_hashtags(ent['hashtags'], tweet_id)
        urls = create_urls(ent['urls'], tweet_id)
        user_mentions = create_user_mentions(ent['user_mentions'], tweet_id)

        # media isn't guarunteed to be present
        try:
            media = create_media(ent['media'], tweet_id)
        except KeyError:
            media = []

        pyobjs['tweets'] += [tweet]
        pyobjs['hashtags'] += hashtags
        pyobjs['media'] += media
        pyobjs['urls'] += urls
        pyobjs['user_mentions'] += user_mentions

    return pyobjs

def get_all_user_ids(tweets, user_mentions):
    """Creates a list of all user_ids in tweets and user_mentions"""
    id_set = set()
    # the user_id of the target
    if tweets: id_set.add(tweets[0].user_id)
    id_set |= set([m.user_id for m in user_mentions])
    id_set |= set([t.in_reply_to_user_id
            for t in tweets if t.in_reply_to_user_id])

    return list(id_set)

# TODO: Can we abstract the method call from the loop in these two factories?
def create_user_json_from_screen_names(twitter_api, screen_names):
    """ Gets the User json objects from Twitter for the given screen_names """
    user_json = []
    start = 0
    length = len(screen_names)
    end = length if length < USER_LIMIT else USER_LIMIT
    while start < length:
        user_json += twitter_api.users.lookup(
                            screen_name=",".join(
                                map(str, screen_names[start:end])))
        start = end
        end = end + USER_LIMIT
    return user_json

def create_user_json_from_user_ids(twitter_api, user_ids):
    """Gets the User json objects from Twitter for the given user_ids"""
    user_json = []
    start = 0
    length = len(user_ids)
    end = length if length < USER_LIMIT else USER_LIMIT
    while start < length:
        user_json += twitter_api.users.lookup(
                            user_id=",".join(map(str, user_ids[start:end])))
        start = end
        end = end + USER_LIMIT
    return user_json

def create_user_pyobjs(user_json):
    """Creates a list of User python objects for the given json objects"""
    return [User(u['created_at'],
                 u['default_profile'],
                 u['default_profile_image'],
                 u['description'],
                 u['favourites_count'],
                 u['followers_count'],
                 u['friends_count'],
                 u['geo_enabled'],
                 u['is_translator'],
                 u['lang'],
                 u['listed_count'],
                 u['location'],
                 u['name'],
                 u['protected'],
                 u['screen_name'],
                 u['statuses_count'],
                 u['time_zone'],
                 u['url'],
                 u['id'],
                 u['id_str'],
                 u['utc_offset'],
                 u['verified'])
            for u in user_json]

#def spy_targets_timeline(screen_name, oauthfile, engine_source,
#                                        user_limit, timeline_limit):
#    oauth = create_oauth(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
#    twitter_api = create_twitter(oauth)
#    session = create_db_session(Base, engine_source, sessionmaker, False)
#
#    if not does_user_exist(session, screen_name):
#        target_user = create_user_json_from_screen_names(twitter_api, [screen_name])
#        user_limit -= 1
#        insert_object_list(session, target_user)
#
#    try:
#        is_user_protected(session, screen_name)
#    except RuntimeError:
#        print("{} is protected and cannot be spied on".format(screen_name))
#        return
#
#    since_id = read_max_tweet_id(session)
#    create_timeline_json(twitter_api, screen_name)
#
