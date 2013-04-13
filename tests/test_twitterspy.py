from twitterspy import oauth_factory
from twitterspy import timeline_json_factory, timeline_pyobj_factory
from twitterspy import CONSUMER_KEY, CONSUMER_SECRET
from twitterspy import API_VERSION, API_DOMAIN
from twitter.api import Twitter

import pytest

def test_oauth_factory(oauthfile, token, token_secret):
    OAuth = oauth_factory(oauthfile, token, token_secret)
    assert OAuth

def test_twitter_factory(oauthfile, token, token_secret):
    twitter_oauth = oauth_factory(oauthfile, token, token_secret)
    twitter_api = None
    if twitter_oauth:
        twitter_api = Twitter(auth=twitter_oauth,
                                secure=True,
                                api_version=API_VERSION,
                                domain=API_DOMAIN)
    assert twitter_api

# expect this to fail with 401 error from twitter b/c of the current token
@pytest.mark.xfail
def test_timeline_json_factory(oauthfile, token, token_secret):
    twitter_oauth = oauth_factory(oauthfile, token, token_secret)
    twitter_api = Twitter(auth=twitter_oauth,
                            secure=True,
                            api_version=API_VERSION,
                            domain=API_DOMAIN)
    screen_name = 'FAKEGRIMLOCK'
    tweet_count = 1
    since_id = None
    max_id = None
    include_rts = True
    exclude_replies = True
    timeline = timeline_json_factory(twitter_api, screen_name, tweet_count, 
                                since_id, max_id, include_rts, exclude_replies)
    assert len(timeline) > 0

# function not yet implemented 
@pytest.mark.xfail
def test_timeline_pyobj_factory(timelinefile):
    with open(timelinefile, 'r') as f:
        timeline_json = json.loads(''.join([line for line in f]))

    timeline_pyobjs = timeline_pyobj_factory(timeline_json)
    assert timeline_pyobs['tweets'][0].screen_name == 'dougstanhope'
