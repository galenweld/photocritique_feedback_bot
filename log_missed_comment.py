# STANDARD LIBRARY IMPORTS
import re
import csv
import os
import datetime
import subprocess
import sys # for args

# THIRD PARTY IMPORTS
import praw

# PROJECT IMPORTS
from setup import reddit
from settings import *
from tools import *
from inbox import check_messages
from reminders import send_reminders

def manually_award_comment(awarding_comment_id):
    awarding_comment = reddit.comment(id=awarding_comment_id)
    print(f'Manually awarding points based on comment {awarding_comment.id} by u/{awarding_comment.author.name}.')
 
    awarded_comment = reddit.comment(id=awarding_comment.parent_id[3:]) if awarding_comment.parent_id[:2]=='t1' else None
    submission      = reddit.submission(id=awarding_comment.link_id[3:])
    
    save_comment_information( awarding_comment, awarded_comment, submission )
    acknowledge_awarding_comment( awarding_comment, awarded_comment, submission )
    if awarding_comment.author.name not in FOLLOWUP_OPTED_OUT_USERS:
        follow_up_with_user( awarding_comment, awarded_comment, submission )
    else:
        print(f'\t/u/{awarding_comment.author.name} has opted out, not messaging.')


if __name__ == '__main__':
    awarding_comment_id = sys.argv[1]
    manually_award_comment( awarding_comment_id )

