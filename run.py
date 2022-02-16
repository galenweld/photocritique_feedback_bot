# STANDARD LIBRARY IMPORTS
import re
import csv
import os
import datetime

# THIRD PARTY IMPORTS
import praw

# PROJECT IMPORTS
from setup import reddit
from settings import *
from tools import *

subreddit = reddit.subreddit(TARGET_SUBREDDIT)

print('Finished initializing. Streaming new comments.')


# STREAM COMMENTS
# for comment in subreddit.stream.comments(pause_after=0):
for comment in subreddit.stream.comments(pause_after=None, skip_existing=True):
    # stream pauses when comment is none when pause_after is set to 0
    # for deployment, set pause_after=None and probably add skip_existing=True
    if comment is None:
        print("Stream paused.")
        break
    
    print(datetime.datetime.now().strftime('[%X %x]'), end='')
    if comment_contains_token( comment ):
        print(f'Awarding points based on comment {comment.id} by u/{comment.author.name}.')
        save_comment_information( comment )
        acknowledge_awarding_comment( comment ) # todo: user flair
        follow_up_with_user( comment ) # todo: implement, including an option to opt out of messages
        
    else:
        print(f'Skipping comment {comment.id} by u/{comment.author.name}.')