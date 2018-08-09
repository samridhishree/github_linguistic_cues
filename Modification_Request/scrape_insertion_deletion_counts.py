# -*- coding: utf-8 -*-
'''
Uses git log to scrape the insertion deletion counts for the commits in the repo
Input: HMM Bursts for the project
Output: Dictionary per project that stores the insertion deletion counts per commit ID
'''

import os
import sys
import subprocess
import cPickle as pickle
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--burst_pickle', help='The pickle file with all bursts of the project', 
                default='Sample_Data/hmm_bursts.pickle')
parser.add_argument('--output_dir', help='Directory containing insertion deletion counts per project', 
                default='Sample_Data/ModRequest/insertion_deletion_counts/')
args, unknown = parser.parse_known_args()

burst_pickle = args.burst_pickle
output_dir = args.output_dir
bursts = pickle.load(open(burst_pickle, 'rb'))
projects = bursts.keys()
projects = ['aio-libs~aioredis', 'idan~oauthlib', 'nilearn~nilearn', 'pycqa~astroid']
cur_dir = os.getcwd()

try:
    os.makedirs(output_dir)
except:
    pass

for project in projects:
    parts = project.split('~')
    owner = parts[0]
    name = parts[1]
    lines = []
    try:
        cd_command = '/usr2/scratch/repo_clones_pypi/' + owner + '/' + name + '/'
        os.chdir(cd_command)
        str = 'git log  --oneline --pretty="@%H"  --stat   |grep -v \| |  tr "\n" " "  |  tr "@" "\n"'
        lines = subprocess.check_output(str, shell=True)
    except Exception as e:
        print "Exception = ", e
    
    if (len(lines)) == 0:
        continue

    print "Processing for project = ", project
    os.chdir(cur_dir)
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
    output_file = os.path.join(output_dir, filename)
    with open(output_file, 'wb') as p_pickle:
        pickle.dump(project_dict, p_pickle)

