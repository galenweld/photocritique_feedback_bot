# this file defines the bi-weekly/monthly discussion thread content

import datetime

from settings import BOT_INFO_URL

now = datetime.date.today()

STICKY_TITLE = f'Photocritique Monthly Award and Discussion Thread - {now.strftime("%B")} {now.strftime("%Y")}'


STICKY_BODY = \
"""
The purpose of these monthly threads is to give shout-outs to the great community members who have been recognized for
providing especially high-quality critiques, and to provide a general-purpose thread to discuss anything about the subreddit
or photography in general.

### Top Community Members

{}

These folks received the most [Critique Points]({}) this month - a huge thanks to them for giving such excellent feedback!

### Top Critique Threads

{}

These threads had the most [Critique Points]({}) awarded in their comments this month. Take a look to find inspiration or
examples of great feedback.

### Discussion

Use this thread to discuss anything about the subreddit or photography in general. Want to know how to imitate an editing style you've seen on someone elses image? Saw some professional work you hate/love and want to discuss? Questions about the rules? Suggestions for how to improve the subreddit? This is thread for you!

If you want an image critiqued or have a question about a specific photo, please review our rules and post that image in its own thread.

Any other questions can be sent directly to the moderators. Thanks!
"""

STICKY_BODY = STICKY_BODY.format(
    '{}',
    BOT_INFO_URL,
    '{}',
    BOT_INFO_URL
)