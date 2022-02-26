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
from inbox import check_messages

subreddit = reddit.subreddit(TARGET_SUBREDDIT)

print('Finished initializing. Streaming new comments.')


# STREAM COMMENTS
for awarding_comment in subreddit.stream.comments(pause_after=5, skip_existing=True):
    # stream pauses when comment is none when pause_after is not None
    # for deployment, set pause_after=None and probably add skip_existing=True

    # stream is paused. check our PMs and send reminders.
    if awarding_comment is None:
        print("Stream paused.")
        check_messages()
        # TODO reminders
        print('Restarting stream. Checking for new comments.')
    
    else:
        # we have a comment, let's process it
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
            if awarding_comment.author.name not in OPTED_OUT_USERS:
                follow_up_with_user( awarding_comment, awarded_comment, submission )
            else:
                print(f'\t/u/{awarding_comment.author.name} has opted out, not messaging.')
            
        else:
            print(f'Skipping comment {awarding_comment.id} by u/{awarding_comment.author.name}.')