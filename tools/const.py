import os

SEARCH_MODES = ["{}", "{}%", "%{}%"]  # Exact match  # Starts with  #

# CSV files - Used to store initial data of EKT application
DICTIONARY_CSV = "ekt_entries.csv"
SCREENS_CSV = "screens.csv"
SCROLL_DIRECTION = "scroll_direction.csv"
CSV_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../csvs/"

# Constants used throughout the application
MAX_ENTRIES = 30
ROW_DEFAULT_HEIGHT = 100
VALID_LANGUAGES = ["kapampangan", "tagalog", "english"]
