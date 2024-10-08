import re
import os

from local_settings import *
# local settings: PATH_TO_STORE

#TARGET_SUBREDDIT = 'phcritiquetest'
TARGET_SUBREDDIT = 'photocritique'

BOT_INFO_URL = 'https://www.reddit.com/r/photocritique/wiki/critiquepoints'

FOLLOWUP_OPTED_OUT_USERS_PATH = os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, 'donotfollowup.txt')
REMINDER_OPTED_OUT_USERS_PATH = os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, 'donotremind.txt')

LAST_PROCESSED_POST_PATH = os.path.join(PATH_TO_STORE, TARGET_SUBREDDIT, 'last_processed_post.txt')

REMINDER_NUM_COMMENTS_THRESHOLD = 4 # a submission must have at least this many comments to recieve a reminder PM

OPTOUT_CONFIRMATION_SUBJECT = 'You have succesfully opted-out of {} about CritiquePoints.'
OUTOUT_CONFIRMATION_BODY = 'Please allow up to 24 hours for this change to go into effect.'

FOLLOWUP_OPTOUT_PATTERN = re.compile(r'optout followups')
REMINDER_OPTOUT_PATTERN = re.compile(r'optout reminders')

FEEDBACK_TOKEN = re.compile('!CritiquePoint', re.IGNORECASE)

ACK_COMMENT = 'Confirmed: 1 [helpfulness point awarded]({awarding_permalink}) to /u/{awardee} by /u/{awarder}.\n\nSee [here]('+BOT_INFO_URL+') for more details on Critique Points.'



# Do not update the flair of users whose most recent points were recieved more than this many hours ago
FLAIR_UPDATE_EXCLUDE_POINTS_OLDER_THAN_HOURS = 48 # set to None to update the flair of all users
USER_FLAIR_TEMPLATE_ID = 'd80fe2f4-9e77-11ec-b748-0e368bf5ca27'

# ensure this is set in moderator settings, then get it using submission.flair.choices()
FLAIR_TEMPLATE_ID = '7eeec638-8f07-11ec-8294-2a47d40d3100' # for phcritiquetest
FLAIR_TEMPLATE_ID = 'aecd47a6-9f03-11ec-bd3c-bed2b38f4d69' # for photocritique


SEGMENTOR = re.compile(r'(\n{2,}|\. |\? |! )')

# time range of posts to remind, in hours
# for now, we're not keeping track of which posts have had reminder messages sent, and just using a narrow time window
# we may wish to address this in the future
REMINDER_LOWER_BOUND, REMINDER_UPPER_BOUND = 48+8,60
assert REMINDER_LOWER_BOUND <= REMINDER_UPPER_BOUND



FOLLOWUP_OPTED_OUT_USERS = set()
if os.path.exists(FOLLOWUP_OPTED_OUT_USERS_PATH):
	with open(FOLLOWUP_OPTED_OUT_USERS_PATH) as f:
		for user in f:
			FOLLOWUP_OPTED_OUT_USERS.add( user.strip() ) # need to ignore the newlines
print(f'Loaded {len(FOLLOWUP_OPTED_OUT_USERS):,d} users who have opted out from follow-ups.')


REMINDER_OPTED_OUT_USERS = set()
if os.path.exists(REMINDER_OPTED_OUT_USERS_PATH):
	with open(REMINDER_OPTED_OUT_USERS_PATH) as f:
		for user in f:
			REMINDER_OPTED_OUT_USERS.add( user.strip() ) # need to ignore the newlines
print(f'Loaded {len(REMINDER_OPTED_OUT_USERS):,d} users who have opted out from reminders.')


# number of weeks to include when looking back at data for weekly sticky posts
WEEKLY_STICKY_THREAD_TIME_PERIOD = 4 # weeks
# note if this is increased to more than 1 month, the sticky script needs to be updated to include more than the two most recent files
# also, if this is changed, you may also want to change the title of the sticky post (in `StickyThreadContent.py`) to "monthly," e.g.

# number of top awardees to include in weekly sticky threads, can be more in case of ties
NUM_TOP_AWARDEES = 3

# number of top threads to inlucde in weekly sticky threads
NUM_TOP_THREADS = 3
