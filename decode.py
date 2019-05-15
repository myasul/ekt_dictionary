#!/usr/bin/env python3
import csv
import re
import sys

CSV_FILENAME = 'ekt_entries.csv'
CSV_FILENAME_OUTPUT = 'ekt_entries_clean.csv'

def decode():
    with open(CSV_FILENAME) as inp, \
            open(CSV_FILENAME_OUTPUT, 'w+', encoding='utf-8') as out:
        writer = csv.writer(out)

        for row in csv.reader(inp):
            for count, word in enumerate(row):
                row[count] = re.sub(r'b\'(.*?)\'', r'\1', word, re.I)
            writer.writerow(row)

def remove_carriage_return():
    with open(CSV_FILENAME) as in_file, \
        open(CSV_FILENAME_OUTPUT, 'w+', encoding='utf-8') as out_file:
        old = in_file.read()
        old.replace(r'\r', '')
        out_file.write(old)

def main():
    # decode()
    remove_carriage_return()


if __name__ == "__main__":
    main()
