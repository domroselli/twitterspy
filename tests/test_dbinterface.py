from dbinterface import *
from tests.helpers import init_db, read_json_file
from tests.helpers import help_create_user_pyobjs_from_file
from tests.helpers import help_create_timeline_pyobjs_from_file
from dbentities import User
#from twitterspy import create_user_pyobjs, create_timeline_pyobjs

import pytest

def test_db_session_factory():
    session = init_db(False)
    result = session.execute('SELECT 1').first()
    assert result[0] == 1

def test_find_unknown_user_ids():
    user_ids = [1,2,3]
    session = init_db(False)
    unknown_user_ids = find_unknown_user_ids(session, user_ids)
    assert  set(user_ids) == set(unknown_user_ids)

def test_insert_object_list(userfile, target_user):
    session = init_db(False)
    user_pyobjs = help_create_user_pyobjs_from_file(userfile)
    session.add_all(user_pyobjs)

    user = session.query(User.screen_name)\
            .filter(User.screen_name == target_user).one()
    assert user[0] == target_user

def test_read_min_tweet_id(userfile, timelinefile, min_tweet_id):
    session = init_db(False)
    user_pyobjs = help_create_user_pyobjs_from_file(userfile)
    session.add_all(user_pyobjs)
    insert_object_list(session, user_pyobjs)

    timeline_pyobjs = help_create_timeline_pyobjs_from_file(timelinefile)
    insert_object_list(session, timeline_pyobjs['tweets'])

    min_id = read_min_tweet_id(session)
    assert min_id == min_tweet_id

def test_read_max_tweet_id(userfile, timelinefile, max_tweet_id):
    session = init_db(False)
    user_pyobjs = help_create_user_pyobjs_from_file(userfile)
    insert_object_list(session, user_pyobjs)

    timeline_pyobjs = help_create_timeline_pyobjs_from_file(timelinefile)
    insert_object_list(session, timeline_pyobjs['tweets'])

    max_id = read_max_tweet_id(session)
    assert max_id == max_tweet_id

def test_does_user_exist(userfile):
    session = init_db(False)
    user_pyobjs = help_create_user_pyobjs_from_file(userfile)
    insert_object_list(session, user_pyobjs)

    screen_name = user_pyobjs[0].screen_name
    assert does_user_exist(session, screen_name)

def test_is_user_protected(userfile):
    session = init_db(False)
    user_pyobjs = help_create_user_pyobjs_from_file(userfile)
    for u in user_pyobjs:
        if not u.protected:
            screen_name = u.screen_name
            break

    insert_object_list(session, [u])

    assert not is_user_protected(session, screen_name)
