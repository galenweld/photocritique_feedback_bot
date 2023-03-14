# STANDARD LIBRARY IMPORTS
import re
import csv
import os
import datetime
import subprocess
from time import sleep

# THIRD PARTY IMPORTS
import praw

# PROJECT IMPORTS
from setup import reddit
from settings import *
from tools import *
from inbox import check_messages
from reminders import send_reminders

subreddit = reddit.subreddit(TARGET_SUBREDDIT)

print('Finished initializing. Streaming new comments.')

def run():
    ''' Infinitely loop over comments and process them.  '''
    # STREAM COMMENTS
    for awarding_comment in subreddit.stream.comments(pause_after=8, skip_existing=True):
        # stream pauses when comment is None when pause_after is not set to None

        # stream is paused. check our PMs and send reminders.
        if awarding_comment is None:
            print(datetime.datetime.now().strftime('[%X %x] '), end='')
            print('Stream paused.')
            check_messages()
            send_reminders()
            print(datetime.datetime.now().strftime('[%X %x] '), end='')
            print('Restarting stream. Checking for new comments.')
        
        else:
            # we have a comment, let's process it
            print(datetime.datetime.now().strftime('[%X %x] '), end='')
            if awarding_comment.author.name != 'AutoModerator' and comment_contains_token( awarding_comment ):
                print(f'Awarding points based on comment {awarding_comment.id} by u/{awarding_comment.author.name}.')

                # Terminology:
                # The comment containing the feedback token is the AWARDING COMMENT and the comment it is directly replying to is
                # the AWARDED COMMENT.
                # check to make sure awarding comment is not a top level comment
                awarded_comment = reddit.comment(id=awarding_comment.parent_id[3:]) if awarding_comment.parent_id[:2]=='t1' else None
                # get the post this discussion is regarding
                submission      = reddit.submission(id=awarding_comment.link_id[3:])

                # until we decide if we are going to permit "self promotion" of CritiquePoints, let's just ignore top-level comments
                if awarded_comment is None:
                    print('Skipping awarding point to top-level comment')
                    continue


                save_comment_information( awarding_comment, awarded_comment, submission )
                acknowledge_awarding_comment( awarding_comment, awarded_comment, submission ) # todo: user flair
                if awarding_comment.author.name not in FOLLOWUP_OPTED_OUT_USERS:
                    follow_up_with_user( awarding_comment, awarded_comment, submission )
                else:
                    print(f'\t/u/{awarding_comment.author.name} has opted out, not messaging.')
                
            else:
                print(f'Skipping comment {awarding_comment.id} by u/{awarding_comment.author.name}.')


if __name__ == '__main__':
    try:
        run()
        sleep(60)

    except Exception as e:
        mail_process = subprocess.Popen(['mail', '-s', 'Error with Photocritique Bot', 'gweld@cs.washington.edu'], stdin=subprocess.PIPE)
        mail_process.communicate( str(e).encode('utf-8') )
        print( 'Emailed crash report.' )
        raise e
