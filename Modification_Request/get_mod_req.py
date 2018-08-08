'''
Inserts a binary feature to the final table telling about the presence/absence of mod request
Based on whether the burst file is present in the filtered list
'''

import os
import sys
import csv
import pandas as pd

congruence_table = sys.argv[1]
mod_req_dir = sys.argv[2]
output_file = sys.argv[3]

data = pd.read_csv(congruence_table)
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
