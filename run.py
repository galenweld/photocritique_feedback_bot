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
for awarding_comment in subreddit.stream.comments(pause_after=None, skip_existing=True):
    # stream pauses when comment is none when pause_after is set to 0
    # for deployment, set pause_after=None and probably add skip_existing=True
    if awarding_comment is None:
        print("Stream paused.")
        break
    
    print(datetime.datetime.now().strftime('[%X %x] '), end='')
    if comment_contains_token( awarding_comment ):
        print(f'Awarding points based on comment {awarding_comment.id} by u/{awarding_comment.author.name}.')

        # Terminology:
        # The comment containing the feedback token is the AWARDING COMMENT and the comment it is directly replying to is
        # the AWARDED COMMENT.
        # check to make sure awarding comment is not a top level comment
        awarded_comment = reddit.comment(id=awarding_comment.parent_id[3:]) if awarding_comment.parent_id[:2]=='t1' else None
        # get the post this discussion is regarding
        submission      = reddit.submission(id=awarding_comment.link_id[3:])


        save_comment_information( awarding_comment, awarded_comment, submission )
        acknowledge_awarding_comment( awarding_comment, awarded_comment, submission ) # todo: user flair
        follow_up_with_user( awarding_comment, awarded_comment, submission ) # todo: implement, including an option to opt out of messages
        
    else:
        print(f'Skipping comment {awarding_comment.id} by u/{awarding_comment.author.name}.')