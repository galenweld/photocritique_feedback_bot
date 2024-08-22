#!/usr/bin/env python
# coding: utf-8

from time import sleep
from glob import glob

# PROJECT IMPORTS
from setup import reddit
from settings import *

# THIRD PARTY IMPORTS
import praw
import pandas as pd


subreddit = reddit.subreddit( TARGET_SUBREDDIT )


# load points
df = pd.concat([
    pd.read_csv(f) for f in glob(os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, 'awards_*.csv'))
])

df['time_since_awarded'] = pd.Timestamp.utcnow() - pd.to_datetime( df.awarding_timestamp, unit='s', utc=True )

num_points = df.groupby( 'awarded_author' ).agg({'awarded_id':'count'}).iloc[:,0]
num_points = num_points.rename('num_critiquepoints')
print(f'Loaded {num_points.sum():,d} critiquepoints from {len(num_points):,d} users.')

post_delay = df.groupby( 'awarded_author' ).agg({'time_since_awarded':'min'}).iloc[:,0]
post_delay = post_delay.rename('time_since_last_award')

if FLAIR_UPDATE_EXCLUDE_POINTS_OLDER_THAN_HOURS is not None:
    users_to_update = post_delay < pd.Timedelta(FLAIR_UPDATE_EXCLUDE_POINTS_OLDER_THAN_HOURS, unit='hours')
    num_points = num_points.reindex( users_to_update.index[users_to_update] )
    print(f"Updating {users_to_update.sum():,d} users' flair", end='')
    print(f"who have received points in the last {FLAIR_UPDATE_EXCLUDE_POINTS_OLDER_THAN_HOURS} hours...")

else:
    print(f"Updating ALL {len(num_points):,d} users' flair...")


for i, (username, score) in enumerate(num_points.items()):
    flair_text = f"{score:,d} CritiquePoint{'s' if score>1 else ''}"
    
    print(f"({(i/len(num_points))*100:5.1f}%) Setting {username}'s flair to `{flair_text}`")
    
    try:
        subreddit.flair.set(
            username,
            flair_template_id=FLAIR_TEMPLATE_ID,
            text=flair_text
        )

        
    except Exception as e:
        print('\tError attempting to set flair, skipping!')
        print(e)
    
    sleep(2)




