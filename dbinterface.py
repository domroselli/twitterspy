from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from email.utils import parsedate_tz
from datetime import datetime, timedelta
from dbentities import User, Tweet

def create_db_session(Base, db_url, sessionmaker, echo_on):
    engine = create_engine(db_url, echo=echo_on)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session()


def find_unknown_user_ids(session, user_ids):
    result = session.query(User.user_id).filter(
                User.user_id.in_(user_ids)).all()
    unknown_users = set(user_ids)
    known_users = set(zip(*result)[0]) if result else set()
    unknown_users = unknown_users - known_users

    return list(unknown_users)


def insert_object_list(session, object_list):
    """
    Inserts a list of database objects to the database using the Session object
    """
    session.add_all(object_list)
    session.commit()


def read_min_tweet_id(session):
    """Returns the minimum tweet_if value from the Tweets table"""
    result = session.query(func.min(Tweet.tweet_id)).one()
    return result[0]


def read_max_tweet_id(session):
    """Returns the maximum tweet_if value from the Tweets table"""
    result = session.query(func.max(Tweet.tweet_id)).one()
    return result[0]


def read_min_tweet_id_greater_than_tweet_id(session, tweet_id):
    """
    Returns the minimum tweet_if value from the Tweets table that is less
    than the passed in tweet_id
    """
    if tweet_id is None:
        tweet_id = 0
    result = session.query(func.min(Tweet.tweet_id)).filter(
            Tweet.tweet_id > tweet_id).one()
    return result[0]


def does_user_exist(session, screen_name):
    result = session.query(User.screen_name).filter(
                User.screen_name == screen_name).one()

    if result:
        return screen_name == result[0]
    else:
        return False


def is_user_protected(session, screen_name):
    result = session.query(User.protected).filter(
                User.screen_name == screen_name).one()

    if not result:
        emsg = "screen_name {} does not exist in database".format(screen_name)
        raise RuntimeError(emsg)

    return result[0]
