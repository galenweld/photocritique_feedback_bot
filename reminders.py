# STANDARD LIBRARY IMPORTS
import re
import datetime

# THIRD PARTY IMPORTS
import praw

# PROJECT IMPORTS
from setup import reddit
from settings import *

subreddit = reddit.subreddit(TARGET_SUBREDDIT)


def send_reminders():
    '''
    Top level function for this module. Loop over recent submissions, and send the OP
    a  PM when appropriate.
    '''
    print('Looking for posts needing reminders.')
    last_processed_post = get_last_processed_post()
    new_last_processed_post = None

    now = datetime.datetime.utcnow() # using utcnow to align with reddit timezone

    for submission in subreddit.new(limit=None):
        submission_age = now - datetime.datetime.fromtimestamp( submission.created_utc )
        submission_age = submission_age.total_seconds() / 60**2 # convert to total hours
#        print(f'Submission {submission.id} {submission.title} has age {submission_age:.1f} hours.')
                
        if submission_age < REMINDER_LOWER_BOUND:
            continue # ignore too-young posts
            
        if (last_processed_post is not None) and (submission.id == last_processed_post):
            print(f'\tStopping at last processed post {submission.id}')
            break
        
        if submission_age > REMINDER_UPPER_BOUND:
            print(f'\tNo last processed post found. Stopping at older post {submission.id}.')
            break
            
        print(f'\tProcessing reminders for post {submission.id}')
        send_reminder(submission)
        if new_last_processed_post is None or (int(submission.id, 36) > int(new_last_processed_post, 36)):
            # keep only the youngest post
            new_last_processed_post = submission.id
    
    # now we're done, store the new last processed post.
    if new_last_processed_post is not None:
        set_last_processed_post(new_last_processed_post)



def get_last_processed_post():
    if os.path.exists(LAST_PROCESSED_POST_PATH):
        with open(LAST_PROCESSED_POST_PATH, 'r') as f:
            return f.read().strip()
    else: return None

def set_last_processed_post(post_id):
    with open(LAST_PROCESSED_POST_PATH, 'w') as f:
        f.write(post_id)
    return


def send_reminder(submission):
    '''
    Send a reminder to the author of the given submission, unless either of the following conditions are met:
    - the author has opted out from reminders, or
    - the submission already has a flair indicating it has recieved HPs from OP
    '''
    if submission.author is None:
        print("\tCannot send reminder to invalid author.")
        return


    if hasattr(submission, 'link_flair_template_id') and (submission.link_flair_template_id == FLAIR_TEMPLATE_ID):
        print(f'\tSkipping sending reminder for submission {submission.id} as it already has points from OP')
        return


    if submission.author.name in REMINDER_OPTED_OUT_USERS:
        print(f'\tSkipping sending reminder for submission {submission.id} as OP /u/{submission.author.name} has opted out.')
        return

    if len( submission.comments.list() ) < REMINDER_NUM_COMMENTS_THRESHOLD:
        print(f"\tSkipping sending reminder for submission {submission.id} as it doesn't have enough comments.")
        return
    
    reminder_subject = f'Did you get good feedback on your photo in /r/{TARGET_SUBREDDIT}?'

    reminder_body = []
    reminder_body.append(f'You recently posted [a photo for critique](https://www.reddit.com{submission.permalink}) in /r/{TARGET_SUBREDDIT}.')
    reminder_body.append('\n')
    reminder_body.append('> '+submission.title)
    reminder_body.append('\n')
    reminder_body.append('I hope you received some useful feedback!')
    reminder_body.append(f"If you did, you can reply to any comment with '{FEEDBACK_TOKEN.pattern}' to give a Critique Point to the person who provided you with a high quality critique.")
    reminder_body.append('Giving Critique Points is easy, and helps improve the whole community.')
    reminder_body.append(f'See [here]({BOT_INFO_URL}) for more information on Critique Points.')
    reminder_body.append('\n')
    reminder_body.append(f"This message was sent by a bot. To opt out of future reminders such as this one, reply to this PM with '{REMINDER_OPTOUT_PATTERN.pattern}'.")
    
    try:
        submission.author.message(reminder_subject, '\n'.join(reminder_body))
        print(f'\tSent reminder PM to /u/{submission.author.name} for "{submission.title}"')
    except praw.exceptions.RedditAPIException as e:
        print("Reddit API exception, skipping.")
        print(e)
    return
