import pytest

def pytest_addoption(parser):
    # token and token_secret borrowed from Mike Verdone's Twitter tools test
    parser.addoption("--oauthfile", action="store", default="tests/oauth_creds",
                     help="file with outh credentials")

    parser.addoption("--token", action="store",
                     default="262332119-7bclllngLikvfVFAqgSe1cRNUE0cnVSYD2YOX7Ju",
                     help="the expected token to be read")

    parser.addoption("--token_secret", action="store",
                     default="aRTJHmcY6szoRLCfHZccTkCqX7yrL3B4fYjwB5ZrI",
                     help="the expected token secret to be read")

    parser.addoption("--timelinefile", action="store", default="tests/timeline.json",
                     help="file with user timeline json data")

    parser.addoption("--userfile", action="store", default="tests/users.json",
                     help="file with user timeline json data")

    parser.addoption("--target_user", action="store", default="DougStanhope",
                     help="the target user to spy on")

    parser.addoption("--min_tweet_id", action="store",
                     default=304529268308856832,
                     help="the minimum tweet_id in the dataset")

    parser.addoption("--max_tweet_id", action="store",
                     default=316216053355143168,
                     help="the maximum tweet_id in the dataset")

    parser.addoption("--user_ids", action="store",
                     default=[14867598,31524680],
                     help="the user_ids to get from twitter to test the user_json factory")

    parser.addoption("--screen_names", action="store",
                     default=["DougStanhope","Ralphie_May"],
                     help="the screen_names to get from twitter to test the user_json factory")

    parser.addoption("--useridfile", action="store", default="tests/userids.json",
                     help="file with outh credentials")

@pytest.fixture
def oauthfile(request):
    return request.config.getoption("--oauthfile")

@pytest.fixture
def token(request):
    return request.config.getoption("--token")

@pytest.fixture
def token_secret(request):
    return request.config.getoption("--token_secret")

@pytest.fixture
def timelinefile(request):
    return request.config.getoption("--timelinefile")

@pytest.fixture
def userfile(request):
    return request.config.getoption("--userfile")

@pytest.fixture
def target_user(request):
    return request.config.getoption("--target_user")

@pytest.fixture
def min_tweet_id(request):
    return request.config.getoption("--min_tweet_id")

@pytest.fixture
def max_tweet_id(request):
    return request.config.getoption("--max_tweet_id")

@pytest.fixture
def screen_names(request):
    return request.config.getoption("--screen_names")

@pytest.fixture
def user_ids(request):
    return request.config.getoption("--user_ids")

@pytest.fixture
def userfile(request):
    return request.config.getoption("--userfile")

@pytest.fixture
def useridfile(request):
    return request.config.getoption("--useridfile")
