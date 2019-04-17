#!/usr/bin/env python2
import requests
import csv
import re
from bs4 import BeautifulSoup
from requests.exceptions import Timeout

BANSA_URL = "http://bansa.org/dictionaries/"\
    "tgl/?dict_lang=tgl&type=search&data={}"


def main():
    with open('kapampangan.csv', 'rb') as inp, \
        open('kapampangan_clean.csv', 'wb+') as out, \
            open('kapampangan_errors.csv', 'wb+') as err:
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
                        writer.writerow(row)

            except (IndexError, Timeout), e:
                writer_err.writer_err(row)


if __name__ == "__main__":
    main()
