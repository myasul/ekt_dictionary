from sqlalchemy import create_engine, asc, inspect, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import sessionmaker
from model.database_setup import Dictionary, Screens, QueryResultMaintainer, Base
from kivy.logger import Logger
from tools.const import SEARCH_MODES

import traceback
import csv
import os

# Connect to the database and create a database session
engine = create_engine("sqlite:///model/ekt_dictionary.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=True)
session = DBSession()

# TODO ::  #1 Add logging
# TODO ::  #2 Add docstring


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def get_all_entries():
    try:
        return (
            session.query(Dictionary).order_by(Dictionary.kapampangan.asc()).all(),
            None,
        )
    except SQLAlchemyError as e:
        Logger.error(f"Error: {traceback.format_exc()}")
        return None, e


def search_in_kapampangan(keyword, mode, count=False, limit=30, offset=0):
    """
    Searches the given Kapampangan word through dictionary.

    Search Mode:
    0 - Exact Match
    1 - Starts With
    2 - Contains
    """
    try:
        if count:
            entry_count = (
                session.query(func.count(Dictionary.kapampangan))
                .filter(Dictionary.kapampangan.like(SEARCH_MODES[mode].format(keyword)))
                .all()
            )
            try:
                return (entry_count[0][0], None)
            except IndexError:
                raise IndexError("Count function did not return any result.")

        return (
            session.query(Dictionary)
            .filter(Dictionary.kapampangan.like(SEARCH_MODES[mode].format(keyword)))
            .order_by(Dictionary.kapampangan.asc())
            .slice(offset, limit + offset)
            .all(),
            None,
        )
    except SQLAlchemyError as e:
        Logger.error(f"Application: {traceback.format_exc()}")
        return None, e
    except IndexError:
        raise IndexError("Invalid Search mode.")


def search_in_tagalog(keyword, mode):
    """
    Searches the given Tagalog word through dictionary.

    Search Mode:
    0 - Exact Match
    1 - Starts With
    2 - Contains
    """
    try:
        return (
            session.query(Dictionary)
            .filter(Dictionary.tagalog.like(SEARCH_MODES[mode].format(keyword)))
            .order_by(Dictionary.tagalog.asc())
            .all(),
            None,
        )
    except SQLAlchemyError as e:
        Logger.error(f"Application: {traceback.format_exc()}")
        return None, e
    except IndexError:
        raise IndexError("Invalid Search mode.")


def search_in_english(keyword, mode):
    """
    Searches the given English word through dictionary.

    Search Mode:
    0 - Exact Match
    1 - Starts With
    2 - Contains
    """
    try:
        return (
            session.query(Dictionary)
            .filter(Dictionary.english.like(SEARCH_MODES[mode].format(keyword)))
            .order_by(Dictionary.english.asc())
            .all(),
            None,
        )
    except SQLAlchemyError as e:
        Logger.error(f"Application: {traceback.format_exc()}")
        return None, e
    except IndexError:
        raise IndexError("Invalid Search mode.")


def search_entry(kapampangan, english, tagalog):
    try:
        return (
            session.query(Dictionary)
            .filter(Dictionary.kapampangan == kapampangan)
            .filter(Dictionary.tagalog == tagalog)
            .filter(Dictionary.english == english)
            .order_by(Dictionary.english.asc())
            .one(),
            None,
        )
    except SQLAlchemyError as e:
        Logger.error(f"Application: {traceback.format_exc()}")
        return None, e


def add_dictionary(entry):
    # TODO :: Incorporate confirmation pop ups when adding entries
    try:
        kapampangan, english, tagalog = entry
        session.add(
            Dictionary(tagalog=tagalog, kapampangan=kapampangan, english=english)
        )
        session.commit()
    except ValueError:
        raise ValueError(
            f"Number of columns from dictionary data"
            f"and table does not match. (expected 3, got {len(entry)})"
        )


def add_screen(screen):
    # TODO :: Incorporate confirmation pop ups when adding entries
    try: 
        name, description = screen
        session.add(Screens(name=name, description=description))
        session.commit()
    except ValueError:
        raise ValueError(
        f"Number of columns from screen data"
            f"and table does not match. (expected 2, got {len(screen)})"
        )

def delete_dictionary(entry):
    session.delete(entry)
    session.commit()

def add_query_result(screen_id, next_row, total_rows):
    try:
        session.add(QueryResultMaintainer(
            screen_id=screen_id,
            next_row=next_row,
            total_rows=total_rows
        ))
        session.commit()
        return (True, None)
    except SQLAlchemyError as e:
        return (False, e)

def update_query_result(next_row):
    qr, error = get_query_result()
    if error:
        return (None, error)

    qr.next_row = next_row
    try:
        session.add(qr)
        session.commit()
        return (True, None)
    except SQLAlchemyError as e:
        return (False, e)

def clean_query_result(screen_id, next_row, total_rows):
    try:
        session.query(QueryResultMaintainer).delete()
        session.commit()
        return (True, None)
    except SQLAlchemyError as e:
        return (False, e)

def get_query_result():
    try:
        qr = session.query(QueryResultMaintainer).one()
    except SQLAlchemyError as e:
        return (None, e)
    else:
        return (qr, None)

def count_dictionary_entries():
    try:
        count = session.query(func.count(Dictionary.kapampangan)).all()
        Logger.info(
            f"Application: There are {count[0][0]} entries" " in the dictionary table."
        )
        return count.pop()[0]
    except Exception:
        Logger.error(f"Application: {traceback.format_exc()}")
        raise
