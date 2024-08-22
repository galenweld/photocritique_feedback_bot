import os

import praw


# CHANGE WORKING DIRECTORY TO THE DIRECTORY CONTAINING THIS FILE
os.chdir( os.path.dirname( os.path.realpath(__file__) ) )

# CONFIGURE REDDIT
reddit = praw.Reddit('pcbot') # using auth info from praw.ini