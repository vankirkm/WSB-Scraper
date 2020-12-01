import praw
import re
import requests
import json
import pandas as pd
import time
import datetime as dt
from praw.models import MoreComments
from psaw import PushshiftAPI
from PushShift import getPushshiftData, collectSubData
from praw import exceptions



# create dictionary of regex patterns to check reference file against
rx_dict = {
    'ticker_calls': re.compile(r'(?P<ticker_calls>[A-Z]+) call'),
    'ticker_puts': re.compile(r'(?P<ticker_puts>[A-Z]+) put'),
    'callPosition': re.compile(r'(?P<callPosition>[A-Z]+) \d+/\d+ \d+[c-cC-C]'),
    'putPosition': re.compile(r'(?P<putPosition>[A-Z]+) \d+/\d+ \d+[p-pP-P]'),
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





# create reddit object with praw, create api with psaw
reddit = praw.Reddit(
    '''personal info censored'''
)



# create list of most recent comment containing regex strings using a comment search with pushshift api
'''api = PushshiftAPI(reddit)
REGEX = r'[A-Z]+'
start_epoch=int(dt.datetime(2020, 11, 24).timestamp())
wsbData = api.search_comments(after=start_epoch, subreddit='wallstreetbets', limit=200)
commentData = []
for c in wsbData:
    commentData.append(c)
for c in commentData:
    print(c, reddit.comment(c).body)'''





# Give URL for thread to parse, create new submission, open reddit_data.txt and prepare to write comments to file
URL = "https://www.reddit.com/r/wallstreetbets/comments/k4ixya/daily_discussion_thread_for_december_01_2020/"
submission = reddit.submission(url=URL)
textData = open(r"F:\\Visual Studio Code Workspace\WSB Scraper\\reddit_data1.txt","r+")


# Get all comments from WSB thread hosted at given URL
'''submission.comments.replace_more(limit=None)
for comment in submission.comments.list():
    textData.write(comment.body.encode('ascii', 'ignore').decode('ascii')+"\n")'''




# parse lines with regex patterns
with textData as file_object:
    line  = file_object.readline()
    numCalls = 0
    numPuts = 0
    numTickerCalls = 0
    numTickerPuts = 0
    data = []
    positionData = []
    numPositions = 0
    while line:
        key, match = parseLine(line)

        # group data by key type
        if key == 'calls':
            numCalls += 1
        elif key == 'puts':
            numPuts += 1
        elif key == 'ticker_calls':
            call_ticker = match.group('ticker_calls', 0)
            numTickerCalls += 1
            row = {
                'Ticker': call_ticker[0],
                'Position': "calls"
            }
            data.append(row)
        elif key == 'ticker_puts':
            numTickerPuts += 1
            put_ticker = match.group('ticker_puts', 0)
            row = {
                'Ticker': put_ticker[0],
                'Position': "puts"
            }
            data.append(row)
        elif key == 'callPosition':
            numPositions += 1
            position = match.group('callPosition', 0)
            row = {
                'Ticker': position[0],
                'Position': re.search(r'\d+/\d+ \d+[c-cC-C]', position[1]).group()
            }
            positionData.append(row)
        elif key == 'putPosition':
            numPositions += 1
            position = match.group('putPosition', 0)
            row = {
                'Ticker': position[0],
                'Position': re.search(r'\d+/\d+ \d+[p-pP-P]', position[1]).group()
            }
            positionData.append(row)           


        line = file_object.readline()
    
# make pandas dataframe for ticker comment volume data   
data = pd.DataFrame(data)
data.set_index(['Ticker'], inplace=True)
data.sort_values(['Ticker'])
data = data.groupby(['Ticker','Position']).agg({'Position': 'count'})
print(data)

# make pandas dataframe for call position comment volume data   
callPositionData = pd.DataFrame(positionData)
callPositionData.set_index(['Ticker'], inplace=True)
callPositionData = callPositionData.groupby(['Ticker','Position']).agg({'Position': 'count'})
print(callPositionData)

# make excel bar chart with pandas dataframe
writer = pd.ExcelWriter(r'F:\\Visual Studio Code Workspace\WSB Scraper\\reddit_data.xlsx', engine='xlsxwriter')
data.to_excel(writer, sheet_name='Sheet1')
callPositionData.to_excel(writer, sheet_name='Sheet2')
numRows = len(data.index)
numPositionRows = len(callPositionData.index)
workbook = writer.book
tickerSheet = writer.sheets['Sheet1']
positionSheet = writer.sheets['Sheet2']
tickerChart = workbook.add_chart({'type': 'column'})
tickerChart.add_series({
    'categories': ['Sheet1', 1, 1, numRows, 0],
    'values':     ['Sheet1', 1, 2, numRows, 2],
    'gap':        2,
})
tickerSheet.insert_chart('D2', tickerChart)

positionChart = workbook.add_chart({'type': 'column'})
positionChart.add_series({
    'categories': ['Sheet2', 1, 1, numPositionRows, 0],
    'values':     ['Sheet2', 2, 2, numPositionRows, 2],
    'gap':        2,
})
positionSheet.insert_chart('D2', positionChart)
writer.save()

print(numCalls, numPuts, numTickerCalls, numTickerPuts, numPositions)


