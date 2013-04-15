from dbinterface import *
from dbentities import Base
from dbentities import Hashtag, Media, Tweet, Timeline, Url, User, UserMention

def test_db_session_factory():
    engine_source = 'sqlite:///:memory:'
    echo_on = False
    session = db_session_factory(Base, engine_source, sessionmaker, echo_on)
    result = session.execute('SELECT 1').first()
    assert result[0] == 1

def test_find_unknown_user_ids():
    user_ids = [1,2,3]
    engine_source = 'sqlite:///:memory:'
    echo_on = False
    session = db_session_factory(Base, engine_source, sessionmaker, echo_on)
    unknown_user_ids = find_unknown_user_ids(session, user_ids)

    assert  set(user_ids) == set(unknown_user_ids)

