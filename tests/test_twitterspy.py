from twitterspy import *
from twitter.api import Twitter

import json
import pytest

def test_oauth_factory(oauthfile, token, token_secret):
    twitter_oauth = oauth_factory(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    assert twitter_oauth

def test_twitter_factory(oauthfile):
    twitter_oauth = oauth_factory(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = None
    if twitter_oauth:
        twitter_api = twitter_factory(twitter_oauth,
                                        API_VERSION, API_DOMAIN, True)
    assert twitter_api

# expect this to fail with 401 error from twitter b/c of the current token
@pytest.mark.skipif("True")
def test_timeline_json_factory(oauthfile):
    twitter_oauth = oauth_factory(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter_factory(twitter_oauth,
                                        API_VERSION, API_DOMAIN, True)
    screen_name = 'FAKEGRIMLOCK'
    tweet_count = 1
    since_id = None
    max_id = None
    include_rts = True
    exclude_replies = True
    timeline = timeline_json_factory(twitter_api, screen_name, tweet_count,
                                since_id, max_id, include_rts, exclude_replies)
    assert len(timeline) > 0

def test_tweet_factory(timelinefile):
    with open(timelinefile, 'r') as f:
        timeline_json = json.loads(''.join([line for line in f]))

    tweets = [tweet_factory(t) for t in timeline_json]
    assert tweets and len(tweets) > 0

def test_hashtags_factory(timelinefile):
    with open(timelinefile, 'r') as f:
        timeline_json = json.loads(''.join([line for line in f]))

    tweet_id = -1
    hashtags = [hashtags_factory(t['entities']['hashtags'], tweet_id)
            for t in timeline_json]
    assert hashtags and len(hashtags) > 0

def test_media_factory(timelinefile):
    with open(timelinefile, 'r') as f:
        timeline_json = json.loads(''.join([line for line in f]))

    tweet_id = -1
    media = [media_factory(t['entities']['media'], tweet_id)
            for t in timeline_json if 'media' in t['entities']]
    assert media and len(media) > 0

def test_urls_factory(timelinefile):
    with open(timelinefile, 'r') as f:
        timeline_json = json.loads(''.join([line for line in f]))

    tweet_id = -1
    urls = [urls_factory(t['entities']['urls'], tweet_id)
            for t in timeline_json]
    assert urls and len(urls) > 0

def test_timeline_pyobj_factory(timelinefile):
    with open(timelinefile, 'r') as f:
        timeline_json = json.loads(''.join([line for line in f]))

    timeline_pyobjs = timeline_pyobj_factory(timeline_json)
    assert timeline_pyobjs
    assert timeline_pyobjs['tweets'] and len(timeline_pyobjs['tweets']) > 0
    assert timeline_pyobjs['hashtags'] and len(timeline_pyobjs['hashtags']) > 0
    assert timeline_pyobjs['media'] and len(timeline_pyobjs['media']) > 0
    assert timeline_pyobjs['urls'] and len(timeline_pyobjs['urls']) > 0

def test_get_all_user_ids(timelinefile):
    with open(timelinefile, 'r') as f:
        timeline_json = json.loads(''.join([line for line in f]))

    timeline_pyobjs = timeline_pyobj_factory(timeline_json)
    tweets = timeline_pyobjs['tweets']
    user_mentions = timeline_pyobjs['user_mentions']
    user_ids = get_all_user_ids(tweets, user_mentions)
    assert len(user_ids) > 0

@pytest.mark.skipif("True")
def test_user_json_factory():
    twitter_ouath = oauth_factory(oauthfile, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter_factory(twitter_oauth,
                                        API_VERSION, API_DOMAIN, True)

    users = user_json_factory(twitter_api, user_ids)
    assert len(users) > 0

def test_user_pyobjs_factory(userfile):
    with open(userfile, 'r') as f:
        user_json = json.loads(''.join([line for line in f]))

    user_pyobjs = user_pyobjs_factory(user_json)
    assert user_pyobjs


