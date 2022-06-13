#!/usr/bin/env python
# coding: utf-8


# STANDARD LIBRARY IMPORTS
import os
import datetime
import glob

# THIRD PARTY IMPORTS
import praw
import pandas as pd

# PROJECT IMPORTS
from setup import reddit
from settings import *
from StickyThreadContent import *

subreddit = reddit.subreddit(TARGET_SUBREDDIT)

# load most recent 2 months worth of awards
recent_awardsfiles = sorted(glob.glob( os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, 'awards*.csv') ), reverse=True)

# last two files
df = pd.concat([pd.read_csv(f) for f in recent_awardsfiles[:2]])

print(f'Loaded {len(df):,d} awards from the past two months')

# filter to recent WEEKLY_STICKY_THREAD_TIME_PERIOD weeks
recency_threshold = datetime.datetime.utcnow() - datetime.timedelta(weeks=WEEKLY_STICKY_THREAD_TIME_PERIOD)
df = df.loc[ df.awarding_timestamp > int(recency_threshold.timestamp()) ,:]

print(f'Filtered to {len(df):,d} awards from the past {WEEKLY_STICKY_THREAD_TIME_PERIOD} weeks.')

# compute top awardees
awardees = df.groupby('awarded_author').agg({'awarding_id':'count'}).iloc[:,0].sort_values(ascending=False)

print(f'Counted awards for {len(awardees):,d} users.')

# include more awardees in case of ties
awardees = awardees.loc[ awardees >= awardees.iloc[NUM_TOP_AWARDEES-1] ]

print(f'Took top {len(awardees):,d} users, considering ties.')

# add '/u/' to start of users, for formatting of reddit table
awardees.index = '/u/' + awardees.index

submissions = df.groupby('submission_id').agg({'awarding_id':'count'}).iloc[:,0].sort_values(ascending=False).iloc[:NUM_TOP_THREADS]
print(f'Got top {NUM_TOP_THREADS:,d} threads with the most awards.')

# fetch submission titles and urls from the api

def format_submission_link(prefixed_id):
    submission = reddit.submission(id=prefixed_id[3:])
    
    try:
        title = submission.title
        link  = submission.permalink
        return f'[{title}](https://reddit.com{link})'
    except:
        return None
    
submissions_formatted = map(format_submission_link, submissions.index)

print('Fetching post titles for top threads, using the reddit API...', end='')
submissions.index = submissions_formatted
print('Done.')


print(f'Dropping {submissions.index.isnull().sum()} threads without titles.')
submissions = submissions.loc[submissions.index.notnull()]


def format_reddit_table(s, header=None, align='--:|:--'):
    '''
    Given a pandas series, format a reddit table with two columns.
    
    The first column is the series index, the second column is the
    series values.
    
    If header is provided, add a header row with the given values.
    As reddit tables require a header, if none is given, a default
    will be included.
    
    for align: :-- is left
               :=: is center
               --: is right
    '''
    assert isinstance(s, pd.Series)
    if header is not None: assert len(header)==2
        
    rows = s.index + ' | ' + s.astype('str')
    
    if header is not None: 
        header = str(header[0]) + ' | ' + str(header[1])
    else:
        header = f'index | {s.name if s.name is not None else "unnamed value"}'
    
    return '\n'.join([header, align]+rows.to_list())
    

awardees    = format_reddit_table(awardees,
                                  header=('Username', 'Points')
                                 )

submissions = format_reddit_table(submissions,
                                  header=('Post Title', 'Awards Within')
                                 )

# silence the deprecation warning
reddit.validate_on_submit = True

print(f'Posting the discussion thread to /r/{TARGET_SUBREDDIT}...', end='')
thread = subreddit.submit(
    title    = STICKY_TITLE,
    selftext = STICKY_BODY.format(awardees, submissions)
)

thread.mod.distinguish()
thread.mod.sticky(bottom=False)
thread.mod.suggested_sort(sort='new')
print('Done.')
