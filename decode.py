#!/usr/bin/env python3
import csv
import re
import sys
import os

CSV_FILENAME = 'ekt_entries.csv'
CSV_FILENAME_OUTPUT = 'ekt_entries_clean.csv'
CSV_FOLDER = f'/csvs/{CSV_FILENAME}'
CSV_OUTPUT_FOLDER = f'/csvs/{CSV_FILENAME_OUTPUT}'
FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def decode():
    with open(FILE_PATH + CSV_FOLDER) as inp, \
            open(FILE_PATH + CSV_OUTPUT_FOLDER, 'w+', encoding='utf-8') as out:
        writer = csv.writer(out)

        for row in csv.reader(inp):
            for count, word in enumerate(row):
                row[count] = re.sub(r'b\'(.*?)\'', r'\1', word, re.I)
            writer.writerow(row)

def remove_carriage_return():
    with open(FILE_PATH + CSV_FOLDER) as in_file, \
        open(FILE_PATH + CSV_OUTPUT_FOLDER, 'w+', encoding='utf-8') as out_file:
        old = in_file.read()
        old.replace(r'\r', '')
        out_file.write(old)

def main():
    # decode()
    remove_carriage_return()


if __name__ == "__main__":
    main()
