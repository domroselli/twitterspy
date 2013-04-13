from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance
from sqlalchemy.orm import sessionmaker
import json

CONSUMER_KEY = 'uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET = 'MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

API_VERSION = "1.1"
API_DOMAIN = "api.twitter.com" 

def do_oauth_dance(oauth_filename, key, secret):
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
        token, token_secret = do_oauth_dance(oauthfile, consumer_key, consumer_secret)

    return OAuth(token, token_secret, consumer_key, consumer_secret)

def twitter_factory(twitter_oauth, api_version=API_VERSION, 
                        api_domain=API_DOMAIN, secure=True):
    return Twitter(auth=twitter_oauth, secure=secure, api_version=api_version,
                    domain=api_domain)

def timeline_json_factory(twitter_api, screen_name, tweet_count, 
        since_id, max_id, include_rts, exclude_replies):
    kwargs = locals()
    return twitter_api.statuses.user_timeline(**kwargs)

def timeline_pyobj_factory(timeline_json):
    pass
