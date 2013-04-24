from dbinterface import create_db_session
from twitterspy import create_timeline_pyobjs, create_user_pyobjs
from twitterspy import create_oauth, create_twitter
from twitterspy import CONSUMER_KEY, CONSUMER_SECRET
from twitterspy import API_VERSION, API_DOMAIN
from dbentities import Base
from sqlalchemy.orm import sessionmaker
import json

def init_db(echo_on=False):
    engine_source = 'sqlite:///:memory:'
    #engine_source = 'sqlite:///test.sqlite'
    return create_db_session(Base, engine_source, sessionmaker, echo_on)

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.loads(''.join([line for line in f]))

def help_create_user_pyobjs_from_file(filename):
    return create_user_pyobjs(read_json_file(filename))

def help_create_timeline_pyobjs_from_file(filename):
    return create_timeline_pyobjs(read_json_file(filename))

def help_create_twitter_api_from_file(oauthfile):
    twitter_oauth = create_oauth(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    return create_twitter(twitter_oauth, API_VERSION, API_DOMAIN, True)
