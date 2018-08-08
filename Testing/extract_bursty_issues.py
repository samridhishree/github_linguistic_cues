'''
Extracts the issues belonging to the bursty periods for projects
'''

import os
import sys
import csv
import glob
import calendar
import cPickle as pickle
import pandas as pd
from collections import defaultdict
from datetime import datetime
import argparse

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--filtered_issue_dir', help='Directory contianing issue threads that have comments related to the Testing tag', 
                default='Sample_Data/Testing/filtered_issue_files/')
parser.add_argument('--output_dir', help='The directory containing burst-wise filtered issue threads. (Issues in the burst that are potentially valid for testing', 
                default='Sample_Data/Testing/burst_filtered_issues/')
parser.add_argument('--project_burst_pickle', help='Pickle containing the project bursts', 
                default='Sample_Data/hmm_bursts.pickle')
args, unknown = parser.parse_known_args()

filtered_issue_dir = args.filtered_issue_dir
output_dir = args.output_dir
project_burst_pickle = args.project_burst_pickle

try:
    os.makedirs(output_dir)
except:
    pass

burst_dict = pickle.load(open(project_burst_pickle, 'rb'))
projects = burst_dict.keys()
colnames = ["rectype", "issueid", "project_owner", "project_name", "actor", "time", "text", "action", "title"]

def ConvertToTime(time_df):
	times = list(time_df)
	formatted_time = []
	for t in times:
		ft = t.split('+')[0]
		t_obj = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
		formatted_time.append(t_obj)
	formatted_series = pd.Series(formatted_time)
	return formatted_series

def FormatBurstTimeInterval(bursts):
	formatted = []
	for i,burst in enumerate(bursts):
		parts= burst.split('-')
		low = parts[0]
		high = parts[1]
		low = low.replace('/', '-')
		high_str = high.replace('/', '-')
		low = datetime.strptime(low, '%Y-%m-%d')
		high = datetime.strptime(high_str, '%Y-%m-%d')
		formatted.append((low, high))
	return formatted

'''
Converts a string time datframe to formatted time dataframe
'''
def ConvertToFormattedTime(time_df):
	times = list(time_df)
	formatted_time = []
	for t in times:
		ft = t.split('+')[0]
		t_obj = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
		formatted_time.append(t_obj)
	formatted_series = pd.Series(formatted_time)
	return formatted_series

'''
Get the issues active in the burst
'''
def GetIssueInBurst(issue_df, burst_start, burst_end):
	times = issue_df['time']
	times.dropna(inplace=True)
	issue_df['formatted_time'] = ConvertToFormattedTime(times)
	sub1 = issue_df.loc[issue_df['formatted_time'] >= burst_start]
	sub2 = sub1.loc[sub1['formatted_time'] <= burst_end]
	return sub2

'''
Extract issues that were either opened or closed during the bursty period
'''
def ExtractAndStoreIssues(bursts, project_name):
	pattern = filtered_issue_dir + '*' + project_name + '_issue*.csv'
	issue_files = glob.glob(pattern)
	if len(issue_files) == 0:
		return
	
	#Get the correct issues with appropriate start and end times
	print "Processing for project : ", project
	valid_issues = defaultdict(list)
	formatted_bursts = FormatBurstTimeInterval(bursts)
	for file in issue_files:
		issue = pd.read_csv(file)#, names=colnames, header=None)
		issue = issue[issue['time'] != 'time']
		issue.fillna('', inplace=True)
		start = issue.loc[issue['action'] == 'start issue']
		close = issue.loc[issue['action'] == 'closed issue']
		if((start.empty == False) and (close.empty == False)):
			start_time = start['time']
			start_time = str(start_time.values[0])
			start_time = start_time.split('+')[0]

			close_time = close['time']
			close_time = str(close_time.values[0])
			close_time = close_time.split('+')[0]

			start_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
			close_obj = datetime.strptime(close_time, '%Y-%m-%d %H:%M:%S')

			for i,burst in enumerate(formatted_bursts):
				low = burst[0]
				high = burst[1]
				if (start_obj.date() >= low.date() and start_obj.date() <= high.date()) or \
				   (close_obj.date() >= low.date() and close_obj.date() <= high.date()):
				   key = "burst_" + str(i)
				   in_burst = GetIssueInBurst(issue, low, high)
				   valid_issues[key].append(in_burst)

	#Store the respective files
	for burst in valid_issues:
		burst_df = pd.concat(valid_issues[burst], axis=0)
		burst_df.to_csv(os.path.join(output_dir, project_name + "_" + burst + '_issues.csv'))

#Extract for the case study commits
# ExtractAndStoreIssues(bokeh_bursts, 'bokeh_bokeh')
# ExtractAndStoreIssues(django_bursts, 'django-extensions_django-extensions')
# ExtractAndStoreIssues(google_bursts, 'google_oauth2client')
# projects = ['rackspace~pyrax', 'darklow~django-suit', 'pazz~alot', 'aio-libs~aioredis', 'idan~oauthlib',\
# 'jtriley~StarCluster', 'plone~plone.dexterity', 'darklow~django-suit']
for project in projects:
	burst = burst_dict[project]
	ExtractAndStoreIssues(burst, project)




			
