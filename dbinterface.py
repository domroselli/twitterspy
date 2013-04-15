from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from email.utils import parsedate_tz
from datetime import datetime, timedelta
from dbentities import User

def db_session_factory(Base, engine_source, session_maker, echo_on):
    engine = create_engine(engine_source, echo=echo_on)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session()

def find_unknown_user_ids(session, user_ids):
    result = session.query(User.user_id)\
                 .filter(User.user_id.in_(user_ids)).all()
    unknown_users = set(user_ids)
    known_users = set(zip(*result)[0]) if result else set()
    unknown_users = unknown_users - known_users

    return list(unknown_users)
