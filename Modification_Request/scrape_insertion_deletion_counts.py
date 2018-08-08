# -*- coding: utf-8 -*-
'''
Uses git log to scrape the insertion deletion counts for the commits in the repo
'''

import os
import sys
import subprocess
import cPickle as pickle
import re

burst_pickle = sys.argv[1]
output_dir = sys.argv[2]
bursts = pickle.load(open(burst_pickle, 'rb'))
projects = bursts.keys()
#projects = projects[0:1]
#git_log_command = 

for project in projects:
    parts = project.split('~')
    owner = parts[0]
    name = parts[1]
    lines = []
    try:
        cd_command = '/usr2/scratch/repo_clones_pypi/' + owner + '/' + name + '/'
        #print cd_command
        os.chdir(cd_command)
        #print os.getcwd()
        str = 'git log  --oneline --pretty="@%H"  --stat   |grep -v \| |  tr "\n" " "  |  tr "@" "\n"'
        lines = subprocess.check_output(str, shell=True)
    except Exception as e:
        print "Exception = ", e
    
    if (len(lines)) == 0:
        continue

    print "Processing for project = ", project
    lines = lines.split('\n')
    project_dict = {}
    for line in lines:
        if(len(line) <= 2):
            continue
        temp = line.split(' ')
        insert_idx = [i for i, s in enumerate(temp) if 'insertion' in s]
        delete_idx = [i for i, s in enumerate(temp) if 'deletion' in s]
        num_insert = 0
        num_delete = 0
        commit_id = temp[0].strip() 
        if len(insert_idx) > 0:
            insert_idx = insert_idx[0]
            num_insert = int(temp[insert_idx-1].strip())
        if len(delete_idx) > 0:
            delete_idx = delete_idx[0]
            num_delete = int(temp[delete_idx-1].strip())
        project_dict[commit_id] = {'insert': num_insert, 'delete': num_delete}

    # Save project dict
    filename = project + '_ins_del_counts.pickle'
    f = open(os.path.join(output_dir, filename), 'wb')
    pickle.dump(project_dict, f)

