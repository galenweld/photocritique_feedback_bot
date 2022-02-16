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



def comment_contains_token(comment):
    '''
    Parse a given comment. If it contains the feedback token, return True.
    '''
    return FEEDBACK_TOKEN.search( comment.body ) is not None



def save_comment_information(awarding_comment):
    '''
    Given a comment containing the feedback token, record to disk the information about this comment and its parents.
    
    Terminology:
    The comment containing the feedback token is the AWARDING COMMENT and the comment it is directly replying to is
    the AWARDED COMMENT.
    '''
    # check to make sure awarding comment is not a top level comment
    awarded_comment = reddit.comment(id=awarding_comment.parent_id[3:]) if awarding_comment.parent_id[:2]=='t1' else None
    # get the post this discussion is regarding
    submission      = reddit.submission(id=awarding_comment.link_id[3:])
    
    comment_info = {
        'awarding_id'             : 't1_'+awarding_comment.id,
        'awarded_id'              : 't1_'+ awarded_comment.id,
        'submission_id'           : 't3_'+       submission.id,
        'awarding_author'         : awarding_comment.author.name,
        'awarded_by_op'           : awarding_comment.author.name==submission.author.name,
        'awarded_author'          : awarded_comment.author.name,
        'submission_author'       : submission.author.name,
        'awarding_timestamp'      : int(awarding_comment.created_utc),
        'awarded_timestamp'       : int(awarded_comment.created_utc),
        'submission_timestamp'    : int(submission.created_utc),
        'awarding_body'           : awarding_comment.body,
        'awarded_body'            : awarded_comment.body,
        'awarded_score'           : awarded_comment.score,
        'submission_score'        : submission.score,
        'submission_url'          : submission.url,
        'submission_title'        : submission.title,
        'submission_num_comments' : submission.num_comments,
        'submission_over_18'      : submission.over_18,
    }
    
    # save this to a file, one per month
    FILE_NAME = datetime.date.today().strftime('awards_%Y_%m.csv')
    FILE_PATH = os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, FILE_NAME)
    
    # need to check if we need to write the header BEFORE we open the file
    write_header = not os.path.exists(FILE_PATH)
    with open(FILE_PATH, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=comment_info.keys())
        if write_header: writer.writeheader()
        writer.writerow(comment_info)
        
        
        
def acknowledge_awarding_comment(awarding_comment):
    '''
    Given an awarding comment it, acknowledge it by replying to it.
    TODO also increment the awardee's flair and flair the submission.
    '''
    # can't award anything when the awarding comment is a top level post, for now we leave this as a no-op
    if awarding_comment.parent_id[:2]=='t3': return
    
    awarded_comment = reddit.comment(id=awarding_comment.parent_id[3:])
    submission      = reddit.submission(id=awarding_comment.link_id[3:])
    
    # make the reply
    reply = awarding_comment.reply(
        ACK_COMMENT.format(**{'awardee':awarded_comment.author.name, 'awarder':awarding_comment.author.name})
    )
    # distinguish it (needs mod permissions)
    reply.mod.distinguish(how='yes')
    
    # HOLDING OFF ON UPDATING AUTHOR FLAIR BECAUSE WE NEED TO MANAGE EXISITING WEBSITE FLAIRS
    
    # flair the submission
    # if this doesn't work, ensure flair visibility is enabled, and that there is a link flair template set
    submission.flair.select(FLAIR_TEMPLATE_ID)
    
    
    
def follow_up_with_user(awarding_comment):
    '''
    todo
    '''
    pass