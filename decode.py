#!/usr/bin/env python3
import csv
import re
import sys

CSV_FILENAME = 'kapampangan_clean.csv'
CSV_FILENAME_OUTPUT = 'kapampangan_decoded.csv'


def main():
    with open(CSV_FILENAME) as inp, \
            open(CSV_FILENAME_OUTPUT, 'w+', encoding='utf-8') as out:
        writer = csv.writer(out)

        for row in csv.reader(inp):
            for count, word in enumerate(row):
                row[count] = re.sub(r'b\'(.*?)\'', r'\1', word, re.I)
            writer.writerow(row)


if __name__ == "__main__":
    main()
