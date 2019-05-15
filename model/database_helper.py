from sqlalchemy import create_engine, asc, inspect
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from model.database_setup import Dictionary, Base
from kivy.logger import Logger

import traceback

# Connect to the database and create a database session
engine = create_engine('sqlite:///model/ekt_dictionary.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=True)
session = DBSession()

# TODO :: Add logging

SEARCH_MODES = [
    "{}",   # Exact match
    "{}%",  # Starts with
    "%{}%"  #
]

DICTIONARY_CSV = 'ekt_entries.csv'
    

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def get_all_entries():
    try:
        return (session.query(Dictionary)
                .order_by(Dictionary.kapampangan.asc())
                .all(), None)
    except SQLAlchemyError as e:
        Logger.info('Error: {}'.format(traceback.format_exc()))
        return None, e


def search_in_kapampangan(keyword, mode):
    '''
    Searches the given Kapampangan word through dictionary.

    Search Mode:
    0 - Exact Match
    1 - Starts With
    2 - Contains
    '''
    try:
        return (session.query(Dictionary)
                .filter(Dictionary.kapampangan.
                        like(SEARCH_MODES[mode].format(keyword)))
                .order_by(Dictionary.kapampangan.asc())
                .all(), None)
    except SQLAlchemyError as e:
        print("Error: {}".format(e))
        return None, e
    except IndexError:
        raise IndexError("Invalid Search mode.")


def search_in_tagalog(keyword, mode):
    '''
    Searches the given Tagalog word through dictionary.

    Search Mode:
    0 - Exact Match
    1 - Starts With
    2 - Contains
    '''
    try:
        return (session.query(Dictionary)
                .filter(Dictionary.tagalog.
                        like(SEARCH_MODES[mode].format(keyword)))
                .order_by(Dictionary.tagalog.asc())
                .all(), None)
    except SQLAlchemyError as e:
        Logger.info('Error: {}'.format(traceback.format_exc()))
        return None, e
    except IndexError:
        raise IndexError("Invalid Search mode.")


def search_in_english(keyword, mode):
    '''
    Searches the given English word through dictionary.

    Search Mode:
    0 - Exact Match
    1 - Starts With
    2 - Contains
    '''
    try:
        return (session.query(Dictionary)
                .filter(Dictionary.english.
                        like(SEARCH_MODES[mode].format(keyword)))
                .order_by(Dictionary.english.asc())
                .all(), None)
    except SQLAlchemyError as e:
        Logger.info('Error: {}'.format(traceback.format_exc()))
        return None, e
    except IndexError:
        raise IndexError("Invalid Search mode.")


def search_entry(kapampangan, english, tagalog):
    try:
        return (session.query(Dictionary)
                .filter(Dictionary.kapampangan == kapampangan)
                .filter(Dictionary.tagalog == tagalog)
                .filter(Dictionary.english == english)
                .order_by(Dictionary.english.asc())
                .one(), None)
    except SQLAlchemyError as e:
        Logger.info('Error: {}'.format(traceback.format_exc()))
        return None, e

def has_dictionary_entries():
    pass

def load_dictionary_entries():
    pass