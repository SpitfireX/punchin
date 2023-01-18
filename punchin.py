#!/usr/bin/env python3

import signal
import os
import csv
import argparse

from time import sleep
from datetime import datetime, timedelta
from pathlib import Path

parser = argparse.ArgumentParser(description='Track time intervals in a CSV file.')
parser.add_argument('-f', type=Path, required=False,
                    default=Path('~/.punchin.csv').expanduser(),
                    help='The CSV file to write time intervals to. Default location: ~/.punchin.csv')

historyfile = parser.parse_args().f

intervals = []
start = datetime.now()
history = []

if historyfile.exists():
    print(f'loading time record file {historyfile}')
    with open(historyfile, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        history = list(reader)
else:
    historyfile.parent.mkdir(parents=True, exist_ok=True)
    print(f'creating new time record file at {historyfile}')

def sigint(signum, frame):
    global intervals, start

    # Make ^C do nothing
    signal.signal(signal.SIGINT, lambda x, y: None)

    now = datetime.now()
    note = input('\nnote for current interval: ')
    intervals.append({'start': start, 'end': now, 'duration': now-start, 'note': note})

    print(f'\npunching out at {now} after {now-intervals[0]["start"]}')
    
    print('intervals recorded:')
    totaltime = timedelta()
    for i in intervals:
        totaltime += i['duration']
        print(f'\t{i["start"]}\t{i["end"]}\t{i["duration"]}\t{i["note"]}')
    
    print(f'total time recorded: {totaltime}')

    with open(historyfile, mode='w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=intervals[0].keys())
        writer.writeheader()
        writer.writerows(history + intervals)

    print(f'wrote record to {historyfile}')

    exit()

def sigtstp(signum, frame):
    global intervals

    now = datetime.now()
    note = input('\nnote for current interval: ')
    intervals.append({'start': start, 'end': now, 'duration': now-start, 'note': note})

    print(f'\npausing at {now}')

    os.system(f'kill -STOP {os.getpid()}')

def sigcont(signum, frame):
    global start

    start = datetime.now()
    print(f'\nresuming at {start}')


signal.signal(signal.SIGINT, sigint)
signal.signal(signal.SIGTSTP, sigtstp)
signal.signal(signal.SIGCONT, sigcont)

print(f'punching in at {start}')

while True:
    sleep(1)
