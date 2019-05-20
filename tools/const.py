import os

SEARCH_MODES = [
    "{}",   # Exact match
    "{}%",  # Starts with
    "%{}%"  #
]

DICTIONARY_CSV = 'ekt_entries.csv'
SCREENS_CSV = 'screens.csv'
CSV_PATH = os.path.dirname(os.path.abspath(__file__)) + '/../csvs/'