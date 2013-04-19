from dbinterface import db_session_factory
from twitterspy import timeline_pyobjs_factory, user_pyobjs_factory
from twitterspy import oauth_factory, twitter_factory
from twitterspy import CONSUMER_KEY, CONSUMER_SECRET
from twitterspy import API_VERSION, API_DOMAIN
from dbentities import Base
from sqlalchemy.orm import sessionmaker
import json

def init_db(echo_on=False):
    engine_source = 'sqlite:///:memory:'
    #engine_source = 'sqlite:///test.sqlite'
    return db_session_factory(Base, engine_source, sessionmaker, echo_on)

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.loads(''.join([line for line in f]))

def create_user_pyobjs(filename):
    return user_pyobjs_factory(read_json_file(filename))

def create_timeline_pyobjs(filename):
    return timeline_pyobjs_factory(read_json_file(filename))

def create_twitter_api(oauthfile):
    twitter_oauth = oauth_factory(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    return twitter_factory(twitter_oauth, API_VERSION, API_DOMAIN, True)
