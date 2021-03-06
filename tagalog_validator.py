#!/usr/bin/env python3
import requests
import csv
import re
import os
from bs4 import BeautifulSoup
from requests.exceptions import Timeout

BANSA_URL = "http://bansa.org/dictionaries/"\
    "tgl/?dict_lang=tgl&type=search&data={}"

CSV_FILENAME = 'kapampangan.csv'
CSV_FILENAME_OUTPUT = 'kapampangan_clean.csv'
CSV_ERR_FILENAME = 'kapampangan_err.csv'
CSV_FOLDER = f'/csvs/{CSV_FILENAME}'
CSV_OUTPUT_FOLDER = f'/csvs/{CSV_FILENAME_OUTPUT}'
CSV_OUTPUT_ERR_FOLDER = f'/csvs/{CSV_ERR_FILENAME}'
FILE_PATH = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(FILE_PATH + CSV_FOLDER, 'r', encoding="utf-8") as inp, \
        open(FILE_PATH + CSV_OUTPUT_FOLDER, 'w', encoding="utf-8") as out, \
            open(FILE_PATH + CSV_OUTPUT_ERR_FOLDER, 'w', encoding="utf-8") as err:
        writer = csv.writer(out)
        writer_err = csv.writer(err)

        for row in csv.reader(inp):
            try:
                # get first word
                word = re.findall(r"\b[a-z]+\b", row[0], re.I)
                if word and len(word) > 0:
                    resp = requests.get(BANSA_URL.format(row[0]), timeout=10)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    tables = soup.find("table")

                    # only add entries that are truly "kapampangan"
                    if not tables:
                        print(
                            f"Processed: {row}")
                        writer.writerow(row)

            except (IndexError, Timeout, UnicodeDecodeError, Exception) as e:
                print(f"Exception: {e}")
                writer_err.writerow(row)


if __name__ == "__main__":
    main()
