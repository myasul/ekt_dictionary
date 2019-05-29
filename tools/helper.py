import csv
import traceback
from kivy import Logger
from timeit import default_timer as timer
from sqlalchemy.exc import SQLAlchemyError
from kivy.app import App

# Internal imports
import model.database_helper as db_helper


def load_data(csv_path, table_name):
    # TODO :: Add docstring
    Logger.info(f"Application: Data migration for {table_name} started.")
    start = timer()
    try:
        with open(csv_path) as f:
            csv_reader = csv.reader(f, delimiter=",")

            for row in csv_reader:

                try:
                    if table_name == "dictionary":
                        db_helper.add_dictionary(row)
                    elif table_name == "screens":
                        db_helper.add_screen(row)
                    elif table_name == "scroll_direction":
                        db_helper.add_scroll_direction(row)
                    else:
                        raise ValueError(f"Invalid table name: {table_name}.")
                except SQLAlchemyError:
                    Logger.error(f"Application: {traceback.format_exc()}")
                    continue
                except ValueError:
                    Logger.error(f"Application: {traceback.format_exc()}")
                    raise

    except Exception:
        Logger.error(f"Application: {traceback.format_exc()}")
        raise
    end = timer()
    Logger.info(
        f"Application: Data migration for {table_name} "
        f"completed in {end-start:.2f} secs."
    )


def create_search_filter_dict(search_str, search_mode=0, language="kapampangan"):
    return {
        "search_str": search_str,
        "search_mode": search_mode,
        "language": language
    }


def get_screen(screen_name):
    screen_manager = App.get_running_app().root
    return screen_manager.get_screen(screen_name)
