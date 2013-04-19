from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from email.utils import parsedate_tz
from datetime import datetime, timedelta
from dbentities import User, Tweet

def db_session_factory(Base, engine_source, sessionmaker, echo_on):
    engine = create_engine(engine_source, echo=echo_on)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session()

def find_unknown_user_ids(session, user_ids):
    result = session.query(User.user_id)\
                 .filter(User.user_id.in_(user_ids)).all()
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
