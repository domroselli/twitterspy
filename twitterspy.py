from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance
from sqlalchemy.orm import sessionmaker

def read_oauthfile(oauth_filename, key, secret):
    """
    Reads the oauth_token and oauth_token_secret from the oauth_filename.
    Returns empty strings for both if the we cannot find them or the user
    doesn't want to create new ones.
    """
    try:
        token, token_secret = read_token_file(oauth_filename)
    except IOError:
        print(('OAuth file {} not found'.format(oauth_filename)))
        request = 'Do you want to initiate a new oauth dance (y or n)? '
        response = raw_input(request)
        if len(response) > 0 and response[0].upper() == 'Y':
            token, token_secret = oauth_dance('Eye spy you!',
                                                key,
                                                secret,
                                                oauth_filename)
        else:
            token = token_secret = ''
    return token, token_secret
