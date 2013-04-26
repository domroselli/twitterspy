from tests.helpers import read_json_file, help_read_users
from tests.helpers import help_create_twitter_api_from_file
from twitterspy import *
from twitter.api import Twitter

import json
import pytest

def test_create_oauth(oauthfile, token, token_secret):
    twitter_oauth = create_oauth(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    assert twitter_oauth


def test_create_twitter(oauthfile):
    twitter_oauth = create_oauth(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = None
    if twitter_oauth:
        twitter_api = create_twitter(
                twitter_oauth, API_VERSION, API_DOMAIN,True)
    assert twitter_api


# This is left disabled to avoid premature rate limiting
#@pytest.mark.skipif("True")
def test_create_timeline_json(oauthfile):
    twitter_api = help_create_twitter_api_from_file(oauthfile)
    timeline_kwargs = { 'screen_name': 'FAKEGRIMLOCK',
                        'tweet_count': 1,
                        'include_rts': True,
                        'exclude_replies': True
                      }
    timeline_json = twitter_api.statuses.user_timeline(**timeline_kwargs)
    assert len(timeline_json) > 0


def test_create_tweet(timelinefile):
    timeline_json = read_json_file(timelinefile)
    tweets = [create_tweet(t) for t in timeline_json]
    assert tweets and len(tweets) > 0


def test_create_hashtags(timelinefile):
    timeline_json = read_json_file(timelinefile)
    tweet_id = -1
    hashtags = [create_hashtags(t['entities']['hashtags'], tweet_id)
                for t in timeline_json]
    assert hashtags and len(hashtags) > 0


def test_create_media(timelinefile):
    timeline_json = read_json_file(timelinefile)
    tweet_id = -1
    media = [create_media(t['entities']['media'], tweet_id)
             for t in timeline_json if 'media' in t['entities']]
    assert media and len(media) > 0


def test_create_urls(timelinefile):
    timeline_json = read_json_file(timelinefile)
    tweet_id = -1
    urls = [create_urls(t['entities']['urls'], tweet_id)
            for t in timeline_json]
    assert urls and len(urls) > 0


def test_create_timeline_pyobjs(timelinefile):
    timeline_json = read_json_file(timelinefile)
    timeline_pyobjs = create_timeline_pyobjs(timeline_json)
    assert timeline_pyobjs
    assert timeline_pyobjs['tweets'] and len(timeline_pyobjs['tweets']) > 0
    assert timeline_pyobjs['hashtags'] and len(timeline_pyobjs['hashtags']) > 0
    assert timeline_pyobjs['media'] and len(timeline_pyobjs['media']) > 0
    assert timeline_pyobjs['urls'] and len(timeline_pyobjs['urls']) > 0


def test_get_all_user_ids(timelinefile):
    timeline_json = read_json_file(timelinefile)
    timeline_pyobjs = create_timeline_pyobjs(timeline_json)
    tweets = timeline_pyobjs['tweets']
    user_mentions = timeline_pyobjs['user_mentions']
    user_ids = get_all_user_ids(tweets, user_mentions)
    assert len(user_ids) > 0


# once dev is stable, remove these. Don't want to eat into the rate limit
@pytest.mark.skipif("True")
def test_create_user_json_from_user_ids(oauthfile, user_ids):
    twitter_api = create_twitter_api(oauthfile)
    user_json = create_user_json_from_user_ids(twitter_api, user_ids)
    assert user_json


@pytest.mark.skipif("True")
def test_create_user_json_from_screen_names(oauthfile, screen_names):
    twitter_api = create_twitter_api(oauthfile)
    user_json = create_user_json_from_screen_names(twitter_api, screen_names)
    assert user_json


def test_create_user_pyobjs(userfile):
    user_json = read_json_file(userfile)
    user_pyobjs = create_user_pyobjs(user_json)
    assert user_pyobjs


@pytest.mark.skipif("True")
def test_create_follower_pyobjs(screen_name, useridfile):
    follower_ids = read_json_file(useridfile)
    follower_pyobj = create_follower_pyobjs(session, screen_name, follower_ids)
    users = help_read_users(follower_ids)
    for u in users:
        assert u.user_id in user_ids


@pytest.mark.skipif("True")
def test_create_follwers(oauthfile, target_user):
    session = init_db()
    twitter_api = help_create_twitter_api_from_file(oauthfile)
    create_followers(twitter_api, session, target_user, 1)
    follower = session.query(Follower).one()
    user = session.query(User).one()
    assert follower.user_id == user.user_id


@pytest.mark.skipif("True")
def test_create_follower_ids(oauthfile, target_user):
    print('authenticating')
    twitter_api = help_create_twitter_api_from_file(oauthfile)
    print('authenticated')
    follower_ids = create_follower_ids(twitter_api, target_user, 1)
    print(follower_ids)
    follower_json = twitter_api.followers.ids(screen_name=target_user, count=1)
    print(follower_json)
    assert(follower_json['ids'][0] == follower_ids[0])


@pytest.mark.skipif("True")
def test_create_follower_pyobjs(oauthfile, target_user):
    twitter_api = help_create_twitter_api_from_file(oauthfile)
    follower_ids = create_follower_ids(twitter_api, target_user, 1)
    assert follower_id[0]
