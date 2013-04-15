from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from email.utils import parsedate_tz
from datetime import datetime, timedelta

def db_session_factory(Base, engine_source, session_maker, echo_on):
    engine = create_engine(engine_source, echo=echo_on)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

