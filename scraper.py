import praw
import re
import pandas as pd
from praw.models import MoreComments

# create dictionary of regex patterns to check reference file against
rx_dict = {
    'ticker_calls': re.compile(r'[A-Z]+ calls'),
    'ticker_puts': re.compile(r'[A-Z]+ puts'),
    'calls': re.compile(r'calls'),
    'puts': re.compile(r'puts')
}

# define function to check for matches against regex dictionary, return the key and the match
def parseLine(line):
    for key, rx in rx_dict.items():
        match = rx.search(line)
        if match:
            print(key)
            print(line)
            return key, match
    return None, None




# create reddit object with praw
reddit = praw.Reddit(
    '''personal data removed'''
)

# Give URL for thread to parse, create new submission, open reddit_data.txt and prepare to write comments to file
URL = "https://www.reddit.com/r/wallstreetbets/comments/jzkpv1/i_made_the_dd_on_ciic_last_week_now_i_am_moving/"
submission = reddit.submission(url=URL)
textData = open(r"F:\Visual Studio Code Workspace\WSB Scraper\reddit_data.txt","r+")


# Get all comments from WSB thread hosted at given URL
submission.comments.replace_more(limit=None)
REGEX = r'/[x{1F601}-x{1F64F}]/u'
for comment in submission.comments.list():
    textData.write(comment.body.encode('ascii', 'ignore').decode('ascii')+"\n")




# parse lines with regex patterns
with textData as file_object:
    line  = file_object.readline()
    numCalls = 0
    numPuts = 0
    numTickerCalls = 0
    numTickerPuts = 0
    while line:
        key, match = parseLine(line)

        # group data by key type
        if key == 'calls':
            numCalls += 1
        elif key == 'puts':
            numPuts += 1
        elif key == 'ticker_calls':
            numTickerCalls += 1
        elif key == 'ticker_puts':
            numTickerPuts += 1
        
        line = file_object.readline()

print(numCalls, numPuts, numTickerCalls, numTickerPuts)



data = []
