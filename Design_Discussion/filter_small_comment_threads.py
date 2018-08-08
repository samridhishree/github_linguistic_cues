'''
For all the issues in the burst, filters out the issues with less than 2 comments and less than 2 distinct members involved in the discussion
'''

import os
import sys
import csv
import pandas as pd


bursty_issues_dir = sys.argv[1]
output_dir = sys.argv[2]

for filename in os.listdir(bursty_issues_dir):
    parts = filename.split('_burst_')
    project = parts[0]
    data = pd.read_csv(os.path.join(bursty_issues_dir, filename))
    title_row = list(data.columns)
    print "Processing for file: ", filename

    # Get all the unique issue ids
    issue_ids = list(set(data['issueid']))
    valid_dfs = []

    # For each issue id get the comments and filter the ones with less than 2 comments or less than 2 people
    for _id in issue_ids:
        issue_data = data.loc[data['issueid'] == _id]
        comments = issue_data.loc[issue_data['rectype'].str.contains('comment')]
        if(comments.empty or comments.shape[0] < 2 or len(list(set(comments['actor']))) < 2):
            continue
        valid_dfs.append(comments)

    # Write the valid comments to the output file
    output_filename = filename.replace('_issues.csv', '_discussions.csv')
    output_file = open(os.path.join(output_dir, output_filename), 'wb')
    writer = csv.writer(output_file)
    writer.writerow(title_row)

    for df in valid_dfs:
        df.sort_values(by='time', inplace=True)
        for idx,row in df.iterrows():
            writer.writerow(list(row))
        writer.writerow([' ']*len(title_row))
        writer.writerow([' ']*len(title_row))
    output_file.close()


