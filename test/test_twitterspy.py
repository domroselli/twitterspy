from twitterspy import *

def test_read_oauthfile():
    known_token = 'requestsecret'
    known_token_secret = 'accesssecret'
    filename = 'oauth_test.txt'
    consumer_key = 'key'
    consumer_secret = 'secret'
    token, token_secret = read_oauthfile(filename, consumer_key, consumer_secret)
    assert token == known_token and token_secret == known_token_secret
