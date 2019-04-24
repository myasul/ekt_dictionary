#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import os
import traceback

BANSA_URL = "http://bansa.org/dictionaries/tgl/?dict_lang=tgl&type=search&data={}"
FILE_PATH = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(FILE_PATH + "/kapampangan_decoded.csv", "r",
              encoding="utf-8") as inp, \
        open(FILE_PATH + "/ekt_entries.csv", "a", encoding="utf-8") as out,\
            open(FILE_PATH + "/ekt_err.csv", "a", encoding="utf-8") as err:
        writer = csv.writer(out)
        writer_err = csv.writer(err)

        for row in csv.reader(inp):
            try:
                # Record time before requesting data from bansa.org
                start = time.time()
                english_word = get_english_word(row[1])

                # Write immediately if there is no valid english word
                if not english_word:
                    print(f"No Translation: {row}")
                    writer.writerow(row)
                    continue

                resp = requests.get(BANSA_URL.format(english_word), timeout=10)
                # Record time before requesting data from bansa.org
                resp_delay = time.time() - start

                # wait 2x longer than it the site to respond
                time.sleep(2 * resp_delay)

                if resp.status_code == 200:
                    print(f"Encoding: {resp.encoding}")
                    row[2] = find_tagalog_in_bansa_table(resp.text)
                    decoded
                    writer.writerow(row)
                    print(f"Processed: {row}")
            except:
                print(traceback.format_exc())
                writer_err.writerow(row)
                print(f"Not Processed: {row}")
                time.sleep(3)
                continue


def get_english_word(words):
    # The function chooses the most appropriate english word
    # to be translated to tagalog. Takes a phrase, a word or group
    # of english words and selects the most appropriate word
    # to be translated.
    if not words:
        return ""

    words = [word.strip().lower() for word in words.split(',')]
    for word in words:
        if len(word.split()) == 1:
            return word


def find_tagalog_in_bansa_table(html):
    # Retrieves the first Tagalog word in a table
    # of results from the English-Tagalog dictionary
    soup = BeautifulSoup(html, "html.parser")
    trans_table = soup.find_all("table")[0]

    for row in trans_table.find_all("tr"):
        columns = row.find_all("td")

        for column in columns:
            tagalog_match = re.search(
                r'Tagalog:\s(.+)$', column.get_text())
            if tagalog_match:
                return tagalog_match.group(1)
    return ""


if __name__ == "__main__":
    main()
