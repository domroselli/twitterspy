import json
import argparse
import sys
import os

from dbentities import Hashtag, Media, Url, UserMention
from dbentities import Base, Tweet, Timeline, User

from dbinterface import read_min_tweet_id, read_max_tweet_id
from dbinterface import create_db_session, insert_object_list
from dbinterface import read_min_tweet_id_greater_than_tweet_id
from dbinterface import find_unknown_user_ids

from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.api import Twitter, TwitterError, TwitterHTTPError
from sqlalchemy.orm import sessionmaker

from pprint import pprint
from time import sleep

CONSUMER_KEY = 'uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET = 'MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

API_VERSION = "1.1"
API_DOMAIN = "api.twitter.com"

USER_LIMIT = 100
TWEET_LIMIT = 200
FOLLOWER_LIMIT = 5000
FRIEND_LIMIT = 5000

DEFAULT_OAUTHFILE = '{}{}.twitter_oauth'.format(os.environ['HOME'], os.sep)
DEFAULT_DB_URL = 'sqlite:///twitterspy-{}.sqlite'

DB_ECHO_ON = False

def do_oauth_dance(oauth_filename, key, secret):
    """ Prompts user to create OAuth token and token secret and then saves them
    in filename
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
    """Creates and OAuth object using the tokens from the oauthfile and the
    consumer_key and consumer_secret. If the file doesn't exists we prompt the
    user to initiate the oauth dance, and save the token and token secret in
    the oauthfile
    """
    try:
        token, token_secret = read_token_file(oauthfile)
    except IOError:
        token, token_secret = do_oauth_dance(oauthfile, consumer_key,
                                                         consumer_secret)

    return OAuth(token, token_secret, consumer_key, consumer_secret)


def create_twitter(twitter_oauth, api_version=API_VERSION,
                        api_domain=API_DOMAIN, secure=True):
    """Creates and returns a Twitter API object"""
    return Twitter(auth=twitter_oauth, secure=secure, api_version=api_version,
                    domain=api_domain)


def create_tweet(tweet_json):
    """Creates a Tweet object"""
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
    """Gets the User json objects from Twitter for the given screen_names"""
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


#def create_follower_ids(twitter_api, screen_name, count=FOLLOWER_LIMIT):
#    """Gets and returns followers json from Twitter"""
#    follower_ids = []
#    cursor = -1
#    backoff_multiplier = 1
#    while cursor != 0:
#        try:
#            follower_json = twitter_api.followers.ids(
#                screen_name=screen_name, count=count)
#            follower_ids += follower_json['ids']
#            cursor = follower_json['next_cursor']
#        except TwitterHTTPError as e:
#            pprint(e)
#            print("waiting {} before trying again...".format(
#                60*backoff_multiplier))
#            sleep(60*backoff_multiplier)
#            backoff_multiplier += 1
#
#    return follower_ids


#def create_followers(twitter_api, session, screen_name, count=FOLLOWER_LIMIT):
#    """Create the users followers in the database"""
#    follower_ids = create_followers_ids(twitter_api, session, screen_name, count)
#    unknown_user_ids = find_unknown_user_ids(session, follower_ids)
#    user_json = create_user_json_from_user_ids(twitter_api, unknown_user_ids)
#    user_pyobjs = create_user_pyobs(user_json)
#    insert_object_list(user_pyobjs)
#
#    follower_pyobjs = create_follower_pyojbs(follower_ids)
#    insert_object_list(follower_pyobjs)
#

#def create_follower_pyobjs(session, screen_name, follower_ids):
#    """Creates follower python objects for the ids"""
#    target_user_id = session.query(User.user_id).filter(
#            User.screen_name == screen_name).one()
#
#    return [Follower(target_user_id, follower_id)
#            for follower_id in follower_ids]
#

def spy_targets_timeline(twitter_api, session, timeline_kwargs):
    """Gets all the Timeline objects from a users timeline and saves them to
    the database
    """

    timeline_json = twitter_api.statuses.user_timeline(**timeline_kwargs)
    timeline_len = len(timeline_json)
    if timeline_len:
        timeline = create_timeline_pyobjs(timeline_json)

        hashtags = timeline['hashtags']
        media = timeline['media']
        tweets = timeline['tweets']
        urls = timeline['urls']
        user_mentions = timeline['user_mentions']

        user_ids = get_all_user_ids(tweets, user_mentions)
        unknown_user_ids = find_unknown_user_ids(session, user_ids)
        user_json = create_user_json_from_user_ids(twitter_api, unknown_user_ids)
        users = create_user_pyobjs(user_json)

        if sys.flags.debug:
            print("Saving {}'s timeline to database".format(screen_name))

        # Order is important due to database dependencies
        if users: insert_object_list(session, users)
        if tweets: insert_object_list(session, tweets)
        if user_mentions: insert_object_list(session, user_mentions)
        if hashtags: insert_object_list(session, hashtags)
        if media: insert_object_list(session, media)
        if urls: insert_object_list(session, urls)

    return timeline_len


def process_command_line(argv):
    """
    Returns a Namespace object with the argument names as attributes.
    `argv`` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """

    if argv is None:
        argv = sys.argv[1:]

    # initialize the parse object
    desc = 'Get Twitter statuses and insert into the database.'
    parser = argparse.ArgumentParser(description=desc)

    t_help = 'The screen_name of the account to monitor'
    parser.add_argument('-s', action='store',
                        dest='screen_name',
                        help=t_help)

    oa_help = 'The filename that has the oauth_token and oauth_token_secret'
    parser.add_argument('-o', action='store',
                        dest='oauthfile',
                        default=DEFAULT_OAUTHFILE,
                        help=oa_help)

    d_help = 'The SQLAlchemy database url to store retrieved data'
    parser.add_argument('-du', action='store',
                        dest='db_url',
                        default=DEFAULT_DB_URL,
                        help=d_help)

    return parser.parse_args()


def _main():
    DB_ECHO_ON = sys.flags.debug
    args = process_command_line(sys.argv)
    screen_name = args.screen_name
    oauthfile = args.oauthfile
    db_url = args.db_url.format(screen_name)

    if screen_name.startswith('@'):
        screen_name = screen_name[1:]

    print("Authenticating to Twitter...")
    oauth = create_oauth(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = create_twitter(oauth)
    print("Authenticated!\n")

    print("Creating session to database: {}".format(db_url))
    session = create_db_session(Base, db_url, sessionmaker, DB_ECHO_ON)
    print("Session established!\n")

    timeline_kwargs = {'screen_name': screen_name,
                       'count': TWEET_LIMIT,
                       'include_rts': True,
                       'exclude_replies': False
                      }
    since_id = read_max_tweet_id(session)
    if since_id is not None:
        timeline_kwargs['since_id'] = since_id

    timeline_len = 1

    print("Getting {}'s timeline...".format(screen_name))
    # For the very first timeline request, since_id is 0 so we'll retrived the
    # entire timeline. Otherwise, we'll return tweets since since_id
    while timeline_len:
        timeline_len = spy_targets_timeline(twitter_api, session, timeline_kwargs)
        max_id = read_min_tweet_id_greater_than_tweet_id(session, since_id)
        timeline_kwargs['max_id'] = max_id - 1

    print("Timeline saved!\n")


if __name__ == '__main__':
    status = _main()
    sys.exit(status)
