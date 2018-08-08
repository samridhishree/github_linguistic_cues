'''
Inserts a binary feature to the final table telling about the presence/absence of mod request
Based on whether the burst file is present in the filtered list
'''

import os
import sys
import csv
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--regression_table', help='The regression table that acts as input to linear regression model', 
                default='Sample_Data/regression_table.csv')
parser.add_argument('--mod_req_dir', help='Directory containing modifcation request filtered files per project', 
                default='Sample_Data/ModRequest/mod_req_files/')
parser.add_argument('--output_file', help='Table with a column attached for presence/absence of modification requests', 
                default='Sample_Data/regression_table_with_mod_request.csv')
args, unknown = parser.parse_known_args()

regression_table = args.regression_table
mod_req_dir = args.mod_req_dir
output_file = args.output_file

data = pd.read_csv(regression_table)
print data.shape
title = list(data.columns)
title.append('mod_request')
w = open(output_file, 'wb')
writer = csv.writer(w)
writer.writerow(title)


for index, row in data.iterrows():
    burst_id = row['burst_id']
    project = row['project']
    print "Processing for project = ", project
    mod_filename1 = project + '_burst_' + str(burst_id) + '_mod_requests.csv'
    mod_filename2 = project.replace('~', '_') + '_burst_' + str(burst_id) + '_mod_requests.csv'
    to_write = list(row)
    if(os.path.isfile(os.path.join(mod_req_dir, mod_filename2)) and os.path.getsize(os.path.join(mod_req_dir, mod_filename2)) != 0):
        try:
            data = pd.read_csv(os.path.join(mod_req_dir, mod_filename2))
            if data.empty:
                to_write.append('N')
            else:
                to_write.append('Y')
        except Exception as e:
            print e   
    elif(os.path.isfile(os.path.join(mod_req_dir, mod_filename1)) and os.path.getsize(os.path.join(mod_req_dir, mod_filename1)) != 0):
        data = pd.read_csv(os.path.join(mod_req_dir, mod_filename1))
        if data.empty:
            to_write.append('N')
        else:
            to_write.append('Y')
    else:
        to_write.append('N')
    writer.writerow(to_write)

w.close()
