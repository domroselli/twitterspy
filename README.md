## TwitterSpy

Store realtime Tweet, User, Follower, and Friend data in a SQL database for any non-protected Twitter account.

__Please Note:__ this software is currently under development and some or all features might not be fully functional just yet.

### Installation
***
**SQLAlchemy**

`pip install sqlalchemy`

**Python Twitter Tools**

`pip install twitter`

### Basic Usage
***
`python twitterspy -s screen_name`

This will run twitterspy against the *screen_name* and store that users Twitter data in a sqlite database named after  
the user in the current working directory 


### Complete Parameter List
***
+ __-s *screen_name*__  
an unprotected screen_name to spy on.

+ __-du *'dabase_url'*__  
   If you want to customize the datastore, you cab confgure the SQLAlchemy Dialect and Pool.  
   See the [SQLAlchemy docs](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls)

+ __-o *twitter_oauthfile*__ 
  By default, TwitterSpy will have your OAuth credentials in a file called .twitterspy_oauth in the current users home directory.  
  If you'd like to use a different oauth file, you can specify one using this parameter.  
  
  *Note:* the OAuth file stores the OAuth token on the first line, and the OAuth secret on the second line of the file.
