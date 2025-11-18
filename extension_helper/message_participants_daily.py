#!/usr/bin/env python
# coding: utf-8


import pandas as pd


from glob import glob
import time
import random


logs = pd.concat([pd.read_json(f, lines=True) for f in glob('/projects/bdata/photocritique-coach-extension/logs/*.jsonl')], axis='rows')
print(f'Loaded {len(logs):d} logs from disk.')


participants = pd.read_csv('/projects/bdata/photocritique-coach-extension/logs/participants.csv')
participants.enrollmentTimestamp = pd.to_datetime(participants.enrollmentTimestamp)
print(f'Loaded {len(participants):d} participants from disk.')


participants['enrollmentDuration'] = pd.Timestamp.utcnow() - participants.enrollmentTimestamp


active   = participants.enrollmentDuration <= pd.Timedelta(days=10)
finished = (participants.enrollmentDuration > pd.Timedelta(days=10)) & (participants.enrollmentDuration <= pd.Timedelta(days=11))
inactive = participants.enrollmentDuration > pd.Timedelta(days=11)

active   = participants.loc[active,:]
finished = participants.loc[finished,:]
inactive = participants.loc[inactive,:]

print(f'Divided into {len(active):,d} active participants, {len(finished):,d} finished participants, and {len(inactive)} inactive participants.')



comments = logs.loc[logs.endpoint=='submitted',:].dropna(how='all', axis='columns')


# get earliest enrollment date for participants to join
comments = pd.merge(comments,
         #           using min here but it shouldn't matter since participants should only be assinged one interface 
         participants.groupby('username').agg({'enrollmentTimestamp':'min','assignedInterface':'min'}).reset_index(),
         how='left',
         left_on='currentUsername',
         right_on='username'
        ).drop('currentUsername', axis='columns')


comments['timeSinceEnrollment'] = comments.timestamp-comments.enrollmentTimestamp
comments['activelyEnrolled'] = comments.timeSinceEnrollment <= pd.Timedelta(days=10)


print(f'Loaded {len(comments):,d} comments made by participants, {comments.activelyEnrolled.sum():,d} were made while they were active in the study.')



# get number of comments made by active users
print('')
print(
    pd.concat([
        active.set_index('username').enrollmentDuration.dt.days.rename('days'),
        comments.loc[comments.activelyEnrolled,:].groupby('username').agg({'timestamp':'count'}).timestamp.rename('comments')
    ], axis='columns').dropna(how='any', subset=['days'], axis='rows').fillna(0).astype('int')
)


# ## get ready to send messages
import sys
sys.path.append('/homes/gws/gweld/photocritique_feedback_bot')
from setup import reddit


EOS_SUBJECT = 'Thanks for trying Photocritique Coach'

EOS_MSG = '''
Thanks for using Photocritique Coach! You've finished your 10 day coaching session, so the extension will automatically
disable itself from your web browser if it hasn't already.

It looks like you wrote {num_comments} comments with help from the coach, thank you!
{flair_yes_no}

We'd love to hear any additional feedback you have about Photocritique Coach.
Please message /u/cyclistNerd if you have comments or questions.
This account can't respond to messages.

You earned {num_tickets} raffle points for participating in our study - but you can earn more!
You can get 1 additional raffle ticket for each comment you write, up to 50 tickets.
**In late-December we'll raffle off a brand new camera of your choice, plus more prizes!**

See [here](https://www.reddit.com/r/photocritique/wiki/browserextension/) for more details on the raffle.
'''

PARTICIPANT_FLAIR_PATH = '/projects/bdata/photocritique-coach-extension/logs/finished_flaired_participants.csv'


# # message people who just finished

print(f'Sending messages to {len(finished):,d} users who finished recently...')
for _, row in finished.iterrows():
    num_comments = comments.loc[comments.username==row.username,'activelyEnrolled'].sum()
    print(f'/u/{row.username} has made {num_comments} comments during their active enrollment.', end=' ')
    
    if num_comments<10:
        flair = "Unfortunately this isn't enough comments to earn a star in your flair."
        print('Not Giving Flair.')
    else:
        flair = "As a shout-out for your hard work, you'll get your star in your flair within an hour or so."
        print('Giving Flair.')
        with open(PARTICIPANT_FLAIR_PATH, 'a') as f:
            f.write(f'{row.username},{str(int(time.time()))}\n')
        
    formatted_message=EOS_MSG.format(
        num_comments=num_comments,
        flair_yes_no=flair,
        num_tickets=min(num_comments, 50),
    )
    
    try:
        print('\tSending end of study message.')
        reddit.redditor(row.username).message(subject=EOS_SUBJECT, message=formatted_message)
        
    except Exception as e:
        print('\tError sending message.')
        print(e)
    time.sleep(2)


# SEND 'HOMEWORK'
# compute posts that have already received a treated comment
posts = comments.loc[comments.activelyEnrolled,:].groupby('postId').agg({'timestamp':'max', 'assignedInterface':set})
posts['most_recent_treatment_activity'] = pd.Timestamp.utcnow() - posts.timestamp
posts = posts.drop('timestamp',axis='columns')


for condition in ['control','assistant','tutor']:
    posts.loc[:,condition] = posts.assignedInterface.apply(lambda l: condition in l)
posts = posts.drop('assignedInterface',axis='columns')


# we only want to suggest posts with some recent activity
posts = posts.loc[posts.most_recent_treatment_activity<=pd.Timedelta(days=5)]
print(f'Filtered to suggesting from {len(posts):,d} posts with a comment within the past 5 days.')


# get filler posts without many comments that we can use if we don't have enough to make recommendations with
posts_with_few_comments = []

subreddit = reddit.subreddit('photocritique')
for submission in subreddit.new(limit=100):  # can increase if needed
    if submission.num_comments < 5:
        posts_with_few_comments.append(submission)

print(f'Found {len(posts_with_few_comments)} posts with < 5 comments')



HOMEWORK_SUBJECT = 'Photocritique Coach: Day {} Reminder!'

HOMEWORK_MSG = '''
Hi u/{username}, thanks for trying out Photocritique Coach!

This is your daily reminder to write some comments using the coach.
According to our records, in the {enrolled_days} day{enrolled_days_plural} you've used the coach,
you've written {num_comments} comment{num_comments_plural}. You need to write at least 10 comments
total to get a star in your flair! You have {days_left} day{days_left_plural} days left to use the coach.
For each comment you write, you'll get an additional raffle ticket to **win a camera**!

Here are some posts that we think could use a comment from you!

'''

HOMEWORK_MSG_END = '''

If you have any questions or feedback, please reach out to /u/cyclistNerd!
This account can't respond to messages.
'''

def message_homework(username, enrollment_duration, posts_to_assign):
    num_comments = comments.loc[comments.username==username,'activelyEnrolled'].sum()
    
    formatted_message = HOMEWORK_MSG.format(
        username      = username,
        enrolled_days = enrollment_duration.days+1,
        enrolled_days_plural = '' if (enrollment_duration.days+1)==1 else 's',
        num_comments = num_comments,
        num_comments_plural = '' if num_comments==1 else 's',
        days_left = 10-enrollment_duration.days,
        days_left_plural = '' if 10-enrollment_duration.days==1 else 's',
    )
    
    for post in posts_to_assign:
        formatted_message += f'* [{post.title}](https://www.reddit.com/r/{post.permalink})\n'
    
    formatted_message += HOMEWORK_MSG_END
    
    reddit.redditor(username).message(
        subject=HOMEWORK_SUBJECT.format(enrollment_duration.days),
        message=formatted_message
    )
    return


print(f'\nSending homework to {len(active)} active participants.')
for _, participant in active.iterrows():
    print(f'/u/{participant.username} ({participant.assignedInterface}) has been enrolled {participant.enrollmentDuration.days} days...')
    
    # get recent posts that no one in this condition has commented on
    eligible_posts = posts.index[~posts.loc[:,participant.assignedInterface]]
    print(f'\tSelecting from {len(eligible_posts)} eligible posts...')
    
    posts_to_assign = [reddit.submission(post_id) for post_id in random.sample(eligible_posts.to_list(), k=min(len(eligible_posts), 3))]
    
    if len(posts_to_assign) < 3:
        needed = 3 - len(posts_to_assign)
        # Make sure we don't try to sample more than available
        available = min(needed, len(posts_with_few_comments))
        print(f'\tAdding {available} posts with few comments.')
        posts_to_assign += random.sample(posts_with_few_comments, k=available)
        
    # send messages
    try:
        print(f'\tMessaging u/{participant.username} with {len(posts_to_assign)} posts')
        message_homework(participant.username, participant.enrollmentDuration, posts_to_assign)
        
    except Exception as e:
        print('\tError sending homework:')
        print(e)
    
    finally:
        time.sleep(2)

