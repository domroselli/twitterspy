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
