# STANDARD LIBRARY IMPORTS
import re
import csv
import datetime

# THIRD PARTY IMPORTS
import praw

# PROJECT IMPORTS
from setup import reddit
from settings import *


SINGLE_NUM_RE = re.compile(r'(\d+)')
NUM_RANGE_RE  = re.compile(r'(\d+) *\- *(\d+)')


def parse_sentence_numbers(s):
    '''
    Given a PM body, parse out the numbers and ranges, ignoring all other characters.
    
    Return set of sentence indices. Convert to a sorted string using ' '.join( map(str, sorted(nums)) )
    '''
    nums = set()
    for low, high in NUM_RANGE_RE.findall(s):
        for num in range(int(low), int(high)+1):
            nums.add( num )
    
    # now when we look for singles, we need to remove the numbers we already got with NUM_RANGE_RE
    for num in SINGLE_NUM_RE.findall( NUM_RANGE_RE.sub('', s) ):
        nums.add( int(num) )
        
    return nums



def process_pm(message):
    '''
    Given a message (PRAW object) check to see if it's an unsubscribe request, otherwise process it.
    '''
    print(f'Processing PM {message.id} from /u/{message.author.name}.')
    for optout_pattern, optout_type, optout_path in ((FOLLOWUP_OPTOUT_PATTERN, 'follow-ups', FOLLOWUP_OPTED_OUT_USERS_PATH), (REMINDER_OPTOUT_PATTERN, 'reminders', REMINDER_OPTED_OUT_USERS_PATH)):
        if optout_pattern.search(message.body) is not None:
            # opt the user out
            with open(optout_path, 'a' if os.path.exists(optout_path) else 'w') as f:
                f.write(message.author.name+'\n')
            # message them to confirm
            message.author.message(OPTOUT_CONFIRMATION_SUBJECT.format(optout_type), OUTOUT_CONFIRMATION_BODY)
            print(f'\tOpted /u/{message.author.name} out from future {optout_type}.')
            return

    else:
        # process the PM assuming it contains sentence number(s) to be recorded.
        sentence_indices = parse_sentence_numbers(message.body)
        if len(sentence_indices) == 0:
            print(f'\tNo sentence indices, skipping.')
            return
        awarded_comment_id = re.search(r'\((\w*)\)', message.subject) # make sure this re stays consistent with the message subject
        if awarded_comment_id is None:
            print(f'\tUnable to locate an awarded comment id in PM subject, skipping.')
            return
        awarded_comment_id = awarded_comment_id[1] # get match group

        # write the span to file, along with the awarded_comment_id and PM timestamp.
        message_info = {
        'awarded_id'              : 't1_'+ awarded_comment_id,
        'message_timestamp'       : int(message.created_utc),
        'sentence_indices'        : ' '.join( map(str, sorted(sentence_indices)) )
        }
        
        # save this to a file, one per month
        FILE_NAME = datetime.date.today().strftime('sentences_%Y_%m.csv')
        FILE_PATH = os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, FILE_NAME)
        
        # need to check if we need to write the header BEFORE we open the file
        write_header = not os.path.exists(FILE_PATH)
        with open(FILE_PATH, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=message_info.keys())
            if write_header: writer.writeheader()
            writer.writerow(message_info)
        print(f'\tStored {len(sentence_indices)} sentence indices for comment {awarded_comment_id} from PM {message.id}.')
        return



def check_messages():
    '''
    Check for unread PMs, and process each of them, marking them as read when done.
    '''
    num_processed = 0

    print('Processing unread PMs.')
    for message in reddit.inbox.unread(limit=None):
        if not isinstance(message, praw.models.Message): continue
            
        process_pm(message)
        message.mark_read()
        num_processed += 1
        
    if num_processed == 0:
        print('Finished. No unread PMs.')
    else:
        print(f'Finished. Processed {num_processed} PMs.')
    return