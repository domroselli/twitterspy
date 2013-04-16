from dbentities import Hashtag, Media, Url, UserMention
from dbentities import Base, Tweet, Timeline, User

from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance
from sqlalchemy.orm import sessionmaker
import json

CONSUMER_KEY = 'uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET = 'MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

API_VERSION = "1.1"
API_DOMAIN = "api.twitter.com"

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

def oauth_factory(oauthfile, consumer_key, consumer_secret):
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

def twitter_factory(twitter_oauth, api_version=API_VERSION,
                        api_domain=API_DOMAIN, secure=True):
    """
    Creates and returns a Twitter API object
    """
    return Twitter(auth=twitter_oauth, secure=secure, api_version=api_version,
                    domain=api_domain)

def timeline_json_factory(twitter_api, screen_name, tweet_count,
        since_id, max_id, include_rts, exclude_replies):
    """
    Gets json object from Twitter and returns it to the caller
    """
    kwargs = locals()
    return twitter_api.statuses.user_timeline(**kwargs)

def tweet_factory(tweet_json):
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
                    tweet_json['retweeted'],
                    tweet_json['source'],
                    tweet_json['retweet_count'],
                    tweet_json['text'],
                    tweet_json['truncated'],
                    tweet_json['id'],
                    tweet_json['id_str'],
                    tweet_json['user']['id'])
    return tweet

def hashtags_factory(hashtag_json, tweet_id):
    """Creates a list of Hashtag objects"""
    return [Hashtag(h['text'], tweet_id) for h in hashtag_json]

def urls_factory(url_json, tweet_id):
    """Creates a list of Url objects"""
    return [Url(u['display_url'], u['expanded_url'], tweet_id, u['url'])
            for u in url_json]

def user_mentions_factory(user_mentions_json, tweet_id):
    """Creates a list of Url objects"""
    return [UserMention(tweet_id, m['id']) for m in user_mentions_json]

def media_factory(media_json, tweet_id):
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

def timeline_pyobj_factory(timeline_json):
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
        tweet = tweet_factory(t)
        tweet_id = tweet.tweet_id
        user_id = tweet.user_id
        ent = t['entities']
        hashtags = hashtags_factory(ent['hashtags'], tweet_id)
        urls = urls_factory(ent['urls'], tweet_id)
        user_mentions = user_mentions_factory(ent['user_mentions'], tweet_id)

        # media isn't guarunteed to be present
        try:
            media = media_factory(ent['media'], tweet_id)
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
    if tweets: id_set.add(tweets[0].user_id)
    id_set |= set([m.user_id for m in user_mentions])
    id_set |= set([t.in_reply_to_user_id
            for t in tweets if t.in_reply_to_user_id])

    return list(id_set)
