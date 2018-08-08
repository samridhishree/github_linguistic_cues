'''
Counts the days of inactivity in a burst by looking at the burst issues and the burst commits
'''

import os
import sys
import csv
import pandas as pd
from datetime import datetime, timedelta, date

csv.field_size_limit(sys.maxsize)

regression_table = sys.argv[1]
burst_issues = sys.argv[2]
burst_commits = sys.argv[3]
output_file = sys.argv[4]

def FormatBurstTime(burst):
	burst = burst.replace('/', '-')
	obj = datetime.strptime(burst, '%Y-%m-%d')
	date_obj = obj.date()
	return date_obj

def ConvertToTime(times):
	formatted_time = []
	for t in times:
		ft = t.split('+')[0]
		if len(ft) == 0 or ft == '[]':
			print "Empty time aborting!!"
			continue
		t_obj = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
		date_obj = t_obj.date()
		formatted_time.append(date_obj)
	formatted_series = pd.Series(formatted_time)
	return formatted_series

def FindNumOfMissingDays(start, end, issue_times, commit_times):
	delta = timedelta(days=1)
	d = start
	missing_days = 0
	while d <= end:
		if (d not in issue_times) and (d not in commit_times):
			missing_days += 1
		d += delta
	return missing_days

data = pd.read_csv(regression_table)
f = open(regression_table, 'rU')
reader = csv.reader(f)
title = next(reader, None)
w = open(output_file, 'wb')
writer = csv.writer(w)
title.append('missing_days')
writer.writerow(title)

for index, row in data.iterrows():
	burst_id = row['burst_id']
	burst_start = row['burst_start']
	burst_end = row['burst_end']

	burst_start_obj = FormatBurstTime(burst_start)
	burst_end_obj = FormatBurstTime(burst_end)
	project = row['project']
	
	print "Processing = ", project
	issue_file_name = project.replace('~', '_') + "_burst_" + str(burst_id) + "_issues.csv"
	commits_file_name = project.replace('~', '_') + "_burst_" + str(burst_id) + "_commits.csv"
	issues = pd.read_csv(os.path.join(burst_issues, issue_file_name))
	commits = pd.read_csv(os.path.join(burst_commits, commits_file_name))
	issue_times = list(issues['time'])
	commit_times = list(commits['time'])
	if len(issue_times) == 0 or len(commit_times) == 0:
		print ("Empty data aborting!!")
		continue
	formatted_issue_times = list(set(ConvertToTime(issue_times)))
	formatted_commit_times = list(set(ConvertToTime(commit_times)))
	missing_days = FindNumOfMissingDays(burst_start_obj, burst_end_obj, formatted_issue_times, formatted_commit_times)
	to_write = list(row)
	to_write.append(missing_days)
	writer.writerow(to_write)





