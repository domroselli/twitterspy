from sqlalchemy import types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from email.utils import parsedate_tz
from datetime import datetime, timedelta

Base = declarative_base()

def to_datetime(datestring):
    """
    Converts the datetime string to a datetime python object.
    """
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


class Hashtag(Base):
    """
    Hashtag class/table that represents hashtags in tweets.
    """
    __tablename__ = 'hashtag'

    hashtag_id = Column(Integer, primary_key=True)
    text = Column(String)
    tweet_id = Column(Integer, ForeignKey('tweets.tweet_id'))

    tweet = relationship("Tweet", backref=backref('hashtags'))

    def __init__(self, text, tweet_id):
        self.text = text
        self.tweet_id = tweet_id

    def __repr__(self):
        return u"<HashtagEntity(''{}', '{}')>".format(self.tweet_id, self.text)


class Media(Base):
    """
    Media class/table that represents media in tweets.
    """
    __tablename__ = 'media'

    display_url = Column(String)
    expanded_url = Column(String)
    media_id = Column(Integer, primary_key=True)
    media_id_str = Column(String)
    media_type = Column(String)
    media_url = Column(String)
    media_url_https = Column(String)
    tweet_id = Column(Integer, ForeignKey('tweets.tweet_id'))
    url = Column(String)

    tweet = relationship("Tweet", backref=backref('media'))

    def __init__(self,
                 display_url,
                 expanded_url,
                 media_id,
                 media_id_str,
                 media_type,
                 media_url,
                 media_url_https,
                 source_status_id,
                 tweet_id,
                 url):

        self.display_url = display_url
        self.expanded_url = expanded_url
        self.media_id = media_id
        self.media_id_str = media_id_str
        self.media_type = media_type
        self.media_url = media_url
        self.media_url_https = media_url_https
        self.source_status_id = source_status_id
        self.tweet_id = tweet_id
        self.url = url

    def __repr__(self):
        return u"<MediaEntity('{}', '{}', '{}')>>".format(self.media_id,
                                                    self.url, self.tweet_id)


class Timeline(Base):
    """
    Timeline class/table that represents tweets in the users timeline
    """
    __tablename__ = 'timeline'

    tweet_id = Column(Integer, ForeignKey('tweets.tweet_id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)

    def __init__(self, tweet_id, user_id):
        self.tweet_id = tweet_id
        self.user_id = user_id


class Tweet(Base):
    """
    Tweet class/table that represents tweets by Twitter users.
    """
    __tablename__ = 'tweets'

    created_at = Column(DateTime)
    favorited = Column(Boolean)
    favorite_count = Column(Integer)
    in_reply_to_screen_name = Column(String)
    in_reply_to_status_id = Column(Integer)
    in_reply_to_status_id_str = Column(String)
    in_reply_to_user_id = Column(Integer)
    in_reply_to_user_id_str = Column(String)
    lang = Column(String)
    possibly_sensitive = Column(Boolean)
    retweet_count = Column(Integer, default='0')
    retweeted = Column(Boolean)
    source = Column(String)
    text = Column(String)
    truncated = Column(Boolean)
    tweet_id = Column(Integer, primary_key=True)
    tweet_id_str = Column(String)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    user = relationship("User", backref=backref('tweets'))

    def __init__(self,
                 created_at,
                 favorited,
                 favorite_count,
                 in_reply_to_screen_name,
                 in_reply_to_status_id,
                 in_reply_to_status_id_str,
                 in_reply_to_user_id,
                 in_reply_to_user_id_str,
                 lang,
                 retweet_count,
                 retweeted,
                 source,
                 text,
                 truncated,
                 tweet_id,
                 tweet_id_str,
                 user_id):

        self.created_at = to_datetime(created_at)
        self.favorited = favorited
        self.favorite_count = favorite_count
        self.in_reply_to_screen_name = in_reply_to_screen_name
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_status_id_str = in_reply_to_status_id_str
        self.in_reply_to_user_id = in_reply_to_user_id
        self.in_reply_to_user_id_str = in_reply_to_user_id_str
        self.lang = lang
        self.retweet_count = retweet_count
        self.retweeted = retweeted
        self.source = source
        self.text = text
        self.truncated = truncated
        self.tweet_id = tweet_id
        self.tweet_id_str = tweet_id_str
        self.user_id = user_id


    def __repr__(self):
        return "<Tweet('{}','{}','{}')>".format(self.tweet_id, self.created_at,
                                           self.text.encode('utf-8', 'ignore'))


class Url(Base):
    """
    Url class/table that represents urls in tweets.
    """
    __tablename__ = 'urls'

    url_id = Column(Integer, primary_key=True)
    display_url = Column(String)
    expanded_url = Column(String)
    tweet_id = Column(Integer, ForeignKey('tweets.tweet_id'))
    url = Column(String)

    tweet = relationship("Tweet", backref=backref('urls'))

    def __init__(self, display_url, expanded_url, tweet_id, url):
        self.display_url = display_url
        self.expanded_url = expanded_url
        self.tweet_id = tweet_id
        self.url = url

    def __repr__(self):
        return u"<Url('{}', '{}')>>".format(self.url, self.tweet_id)


class User(Base):
    """
    User class/table that represents users of Twitter.
    """
    __tablename__ = 'users'

    # we can't always guarantee we can get user data from Twitter, so fields
    # that are nomally not nullable will have to be to prevent data loss
    created_at = Column(DateTime)
    default_profile = Column(Boolean)
    default_profile_image = Column(Boolean)
    description = Column(String)
    favourites_count = Column(Integer, default='0')
    followers_count = Column(Integer, default='0')
    follow_request_sent = Column(Boolean)
    friends_count = Column(Integer, default='0')
    geo_enabled = Column(Boolean)
    lang = Column(String)
    listed_count = Column(Integer)
    location = Column(String)
    id_str = Column(String, default='0')
    is_translator = Column(Boolean)
    name = Column(String)
    protected = Column(Boolean)
    screen_name = Column(String)
    statuses_count = Column(Integer)
    time_zone = Column(String)
    url = Column(String)
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    utc_offset = Column(Integer)
    verified = Column(Boolean)

    def __init__(self,
            created_at,
            default_profile,
            default_profile_image,
            description,
            favourites_count,
            followers_count,
            friends_count,
            geo_enabled,
            is_translator,
            lang,
            listed_count,
            location,
            name,
            protected,
            screen_name,
            statuses_count,
            time_zone,
            url,
            user_id,
            user_id_str,
            utc_offset,
            verified):

            self.created_at = to_datetime(created_at)
            self.default_profile = default_profile
            self.default_profile_image = default_profile_image
            self.description = description
            self.favourites_count = favourites_count
            self.followers_count = followers_count
            self.friends_count = friends_count
            self.geo_enabled = geo_enabled
            self.is_translator = is_translator
            self.lang = lang
            self.listed_count = listed_count
            self.location = location
            self.name = name
            self.protected = protected
            self.screen_name = screen_name
            self.statuses_count = statuses_count
            self.time_zone = time_zone
            self.url = url
            self.user_id = user_id
            self.user_id_str = user_id_str
            self.utc_offset = utc_offset
            self.verified = verified

    def __repr__(self):
        return "<User('{}','{}', '{}')>".format(self.user_id, self.created_at,
                                        self.name.encode('utf-8', 'ignore'))


class UserMention(Base):
    """
    UserMention class/table that represents mentions in tweets.
    """
    __tablename__ = 'usermentions'

    user_mention_id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey('tweets.tweet_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))

    tweet = relationship("Tweet", backref=backref('user_mentions'))

    def __init__(self, tweet_id, user_id):
        self.tweet_id = tweet_id
        self.user_id = user_id

    def __repr__(self):
        return u"<UserMention('{}', '{}')>>".format(self.tweet_id, self.user_id)


