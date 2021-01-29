from pandas.tseries import offsets
import praw
import pathlib
import os
import re
import requests
import json
import pandas as pd
import time
import datetime as dt
from datetime import timedelta, date
from praw.models import MoreComments
from psaw import PushshiftAPI
from requests.api import put
from PushShift import getPushshiftData, collectSubData
from praw import exceptions
import yfinance as yf


# define function to iterate over days 
def daterange(startDate, endDate):
    for n in range(((endDate - startDate)).days):
        yield startDate + timedelta(n)

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
            return key, match
    return None, None



# create reddit object with praw, create api with psaw
reddit = praw.Reddit(
    '''removed'''
)



# get all comments from designated subreddit within a date range and save to disk.
'''startDate = date(2020, 12, 7)
endDate = date(2020, 12, 8)
date_range = daterange(startDate, endDate)
api = PushshiftAPI(reddit)

start = dt.datetime
for date in date_range:
    print(date)
    endTemp = date + timedelta(days=1)
    start_stamp = int(time.mktime(date.timetuple()))
    
    end_stamp = int(time.mktime(endTemp.timetuple()))
    print(start_stamp, end_stamp)
    wsbData = api.search_comments(after=start_stamp, before=end_stamp, subreddit='wallstreetbets')
    comment_data = open(r"F:\\Visual Studio Code Workspace\\WSB Scraper\\reddit_data\\12 - December\\%s.txt" %date , "w+", encoding="utf-8")
    with comment_data as file_object:
        for c in wsbData:
            comment_data.write(c.body + "\n")'''





# Give URL for thread to parse, create new submission, open reddit_data.txt and prepare to write comments to file
'''URL = "https://www.reddit.com/r/wallstreetbets/comments/k5vaj4/daily_discussion_thread_for_december_03_2020/"
submission = reddit.submission(url=URL)
textData = open(r"F:\\Visual Studio Code Workspace\\WSB Scraper\\reddit_data\\reddit_data.txt","r+")'''


# Get all comments from WSB thread hosted at given URL
'''submission.comments.replace_more(limit=None)
for comment in submission.comments.list():
    textData.write(comment.body.encode('ascii', 'ignore').decode('ascii')+"\n")'''


list_subfolders_with_paths = [f.path for f in os.scandir(r'F:\Visual Studio Code Workspace\WSB Scraper\reddit_data') if f.is_dir()]
for folder in list_subfolders_with_paths:
    for comment_file in os.listdir(folder):
        print(comment_file)
        textData = open(folder + "\\" + comment_file, encoding="utf-8")



        # parse lines with regex patterns. There are currently a lot of unnecessary arrays being used
        # while I figure out the best way to handle mapping puts/calls to excel charts. 
        with textData as file_object:
            line  = file_object.readline()
            numCalls = 0
            numPuts = 0
            numTickerCalls = 0
            numTickerPuts = 0
            callData = []
            putData = []
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
                    callData.append(row)
                elif key == 'ticker_puts':
                    numTickerPuts += 1
                    put_ticker = match.group('ticker_puts', 0)
                    row = {
                        'Ticker': put_ticker[0],
                        'Position': "puts"
                    }
                    putData.append(row)
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
        if(callData or putData):   
            callData = pd.DataFrame(callData)
            putData = pd.DataFrame(putData)
            callData.set_index(['Ticker'], inplace=True)
            callData.sort_values(['Ticker'])
            callData = callData.groupby(['Ticker','Position']).agg({'Position': 'count'})
            putData.set_index(['Ticker'], inplace=True)
            putData.sort_values(['Ticker'])
            putData = putData.groupby(['Ticker','Position']).agg({'Position': 'count'})

            # make pandas dataframe for call position comment volume data   
            callPositionData = pd.DataFrame(positionData)
            callPositionData.set_index(['Ticker'], inplace=True)
            callPositionData = callPositionData.groupby(['Ticker']).agg({'Position': 'count'})

            # make excel bar chart with pandas dataframe 
            folder_name = os.path.split(folder)[1]
            file_name = os.path.splitext(comment_file)[0]
            if(os.path.isdir(r'F:\\Visual Studio Code Workspace\\WSB Scraper\\excel_data\\%s'%folder_name) == False):
                os.makedirs(r'F:\\Visual Studio Code Workspace\\WSB Scraper\\excel_data\\%s'%folder_name)
            writer = pd.ExcelWriter(r'F:\\Visual Studio Code Workspace\\WSB Scraper\\excel_data\\%s\\%s.xlsx' %(folder_name, file_name), engine='xlsxwriter')
            callData.to_excel(writer, sheet_name='Sheet1')
            putData.to_excel(writer, sheet_name='Sheet1', startcol=3)
            callPositionData.to_excel(writer, sheet_name='Sheet2')
            numCallRows = len(callData.index)
            numPutRows = len(putData.index) 
            numPositionRows = len(callPositionData.index)
            workbook = writer.book
            tickerSheet = writer.sheets['Sheet1']
            positionSheet = writer.sheets['Sheet2']
            tickerChart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
            tickerChart.add_series({
                'name': ['Sheet1', 0, 1],
                'categories': ['Sheet1', 1, 1, numCallRows, 0],
                'values':     ['Sheet1', 1, 2, numCallRows, 2],
                'gap':        2,
            })
            tickerChart.add_series({
                'name': ['Sheet1', 0, 1],
                'categories': ['Sheet1', 4, 4, numPutRows, 3],
                'values':     ['Sheet1', 4, 5, numPutRows, 5],
                'gap':        2,
            })
            tickerSheet.insert_chart('O2', tickerChart)

            positionChart = workbook.add_chart({'type': 'column'})
            positionChart.add_series({
                'categories': ['Sheet2', 1, 1, numPositionRows, 0],
                'values':     ['Sheet2', 2, 2, numPositionRows, 2],
                'gap':        2,
            })
            positionSheet.insert_chart('D2', positionChart)
            writer.save()



