from sqlalchemy import create_engine, asc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from database_setup import Dictionary, Base

# Connect to the database and create a database session
engine = create_engine('sqlite:///ekt_dictionary.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=True)
session = DBSession()

# TODO :: Add logging


def get_all_entries():
    try:
        return session.query(Dictionary)\
            .order_by(Dictionary.kapampangan.asc())\
            .all(), None
    except IntegrityError as e:
        return None, e
