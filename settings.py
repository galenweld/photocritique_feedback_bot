import re
import os

from local_settings import *
# local settings: PATH_TO_STORE, OPTED_OUT_USERS_PATH

TARGET_SUBREDDIT = 'phcritiquetest'

OPTED_OUT_USERS_PATH = os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, 'donotmessage.txt')

OPTED_OUT_USERS = set()
if os.path.exists(OPTED_OUT_USERS_PATH):
	with open(OPTED_OUT_USERS_PATH) as f:
		for user in f:
			OPTED_OUT_USERS.add( user.strip() ) # need to ignore the newlines
print(f'Loaded {len(OPTED_OUT_USERS):,d} users who have opted out.')

OPTOUT_CONFIRMATION_SUBJECT = 'You have succesfully opted-out of messages about CritiquePoints.'
OUTOUT_CONFIRMATION_BODY = 'Please allow up to 24 hours for this change to go into effect.'

FEEDBACK_TOKEN = re.compile('#helpful')

ACK_COMMENT = 'Confirmed: 1 [helpfulness point awarded]({awarding_permalink}) to /u/{awardee} by /u/{awarder}.\n\nTODO: ^(Link to explaination post.)'

# ensure this is set in moderator settings, then get it using submission.flair.choices()
FLAIR_TEMPLATE_ID = '7eeec638-8f07-11ec-8294-2a47d40d3100'


SEGMENTOR = re.compile(r'(\n{2,}|\. |\? |! )')

OPTOUT_PATTERN = re.compile(r'optout')
