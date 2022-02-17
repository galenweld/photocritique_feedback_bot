import re
from local_settings import *
# local settings: PATH_TO_STORE, 

TARGET_SUBREDDIT = 'phcritiquetest'

FEEDBACK_TOKEN = re.compile('#helpful')

ACK_COMMENT = 'Confirmed: 1 helpfulness point awarded to /u/{awardee} by /u/{awarder}.\n\nTODO: ^(Link to explaination post.)'

# ensure this is set in moderator settings, then get it using submission.flair.choices()
FLAIR_TEMPLATE_ID = '7eeec638-8f07-11ec-8294-2a47d40d3100'


SEGMENTOR = re.compile(r'(\n{2,}|\. |\? )')
