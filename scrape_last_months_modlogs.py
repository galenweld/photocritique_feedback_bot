#!/usr/bin/env python
# coding: utf-8

# STANDARD LIBRARY IMPORTS
import os
import datetime
import glob
import json

# THIRD PARTY IMPORTS
import praw
import pandas as pd

# PROJECT IMPORTS
from setup import reddit
from settings import *

subreddit = reddit.subreddit(TARGET_SUBREDDIT)


OUTPUT_PATH = os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, 'modlogs')

TARGET_MONTH = (datetime.date.today()-datetime.timedelta(days=27)).month
TARGET_YEAR  = (datetime.date.today()-datetime.timedelta(days=27)).year
TARGET_STRING = f'{TARGET_YEAR:04d}_{TARGET_MONTH:02d}'
# using string comparison for easy month/year disambiguation


modlogs = []
for ma in subreddit.mod.log(limit=None):
    # assumes modlogs will be sorted chronologically
    timestamp = datetime.datetime.fromtimestamp( ma.created_utc )
    ml_month = f'{timestamp.year:04d}_{timestamp.month:02d}'
    
    if ml_month < TARGET_STRING:
        # we're done, stop
        break
    
    elif ml_month == TARGET_STRING:
        # keep
        modlogs.append(ma)
    
    else:
        # ignore (too recent)
        continue
print(f'Downloaded {len(modlogs):,d} modlogs for {datetime.date(year=2000, month=TARGET_MONTH, day=1).strftime("%B")}.')


def write_modaction_to_file(ma):
    '''
    given a ModAction, write it to a nice line-delineated json
    file in OUTPUT_PATH, following the naming convention:
    "ML_YEAR_MONTH" e.g. ML_2022_05 for May 2022
    '''
    
    timestamp = datetime.datetime.fromtimestamp( ma.created_utc )
    
    outfile = os.path.join(OUTPUT_PATH, timestamp.strftime('ML_%Y_%m'))
    
    out = {k if k!='_mod' else 'mod':v for k,v in vars(ma).items() if k!='_reddit'}
    
    with open(outfile, 'a') as f:
        f.write( json.dumps(out) + '\n' )


for ma in modlogs:
    write_modaction_to_file(ma)
print(f'Wrote {len(modlogs):,d} modlogs to {OUTPUT_PATH}.')

