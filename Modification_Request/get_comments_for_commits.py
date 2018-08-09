'''
Reads the csv files representing the issue activities that occur in a burst.
Finds out the PR commits that occur after a PR was opened.
Gets the comments with highest similarity for each PR commit in that aprticular PR that occured before the commit itself
'''

import fastText.FastText as fasttext
import os
import sys
import numpy as np
from collections import defaultdict
import cPickle as pickle
import pandas as pd
import csv
from scipy import spatial
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import string
import codecs
import argparse

csv.field_size_limit(sys.maxsize)
reload(sys)
sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser()
parser.add_argument('--bursty_issues_dir', help='Folder containing burst wise issues', 
                default='Sample_Data/burst_issues/')
parser.add_argument('--raw_commit_dir', help='Directory containing raw commit files per project', 
                default='Sample_Data/raw_commits/')
parser.add_argument('--ins_del_count_dir', help='Directory containing insertion/deletion counts per commit per project', 
                default='Sample_Data/ModRequest/insertion_deletion_counts/')
parser.add_argument('--trained_model', help='Path for trained FastText Model', 
                default='/usr2/scratch/sschoudh/FastText/trained_model/wiki.en.bin')
parser.add_argument('--output_dir', help='Directory containing modifcation request filtered files per project', 
                default='Sample_Data/ModRequest/mod_req_files/')
args, unknown = parser.parse_known_args()

CHAR_THRESHOLD = 25
bursty_issues_dir = args.bursty_issues_dir
raw_commit_dir = args.raw_commit_dir
ins_del_count_dir = args.ins_del_count_dir
trained_model = args.trained_model     #FastText Model
output_dir = args.output_dir
MAX_LEN = 400

try:
    os.makedirs(output_dir)
except:
    pass

def CleanIssueComment(text):
    i=text.find('~~')    
    while (i>=0):
        endi=i+2+text[i+2:].find('~~')
        if endi==i+1: text=text[:i]
        else: text=text[:i]+text[endi+2:]
        i=text.find('~~')

    #Remove code snippets
    i=text.find('```')
    while (i>=0):
        endi=i+3+text[i+3:].find('```')
        if endi==i+2:
            text=text[:i]
        else:
            text=text[:i]+' {code} '+text[endi+3:]
        i=text.find('```')

    i=text.find('`')
    while (i>=0):
        endi=i+1+text[i+1:].find('`')
        if endi==i:
            text=text[:i]
        else:
            text=text[:i]+' {code} '+text[endi+1:]
        i=text.find('`')

    i=text.find('>')
    while (i>=0):
        endi=i+text[i:].find('\n')
        if endi==i-1: text=text[:i]
        else: text=text[:i]+text[endi+1:]
        i=text.find('>')

    #Find and extract URLs
    text = re.sub(r'http\S+', '{url}', text, flags=re.MULTILINE)
    
    # Remove {url} and {code} tags
    text = text.replace('{url}', '')
    text = text.replace('{code}', '')

    # Strip punctuation
    text = text.translate(None, string.punctuation)

    text=text.replace('*','')
    text=text.replace('[','')
    text=text.replace(']','')
    text=text.replace('(','')
    text=text.replace(')','')
    text=text.replace('{','')
    text=text.replace('}','')
    text=text.replace('\\',' ')
    text=text.replace('<',' ')
    text=text.replace('>',' ')
    text=text.replace('`',' ')
    text=text.replace('"',' ')
    text = text.replace('\n', ' ').replace('\r', '')    

    #Remove non utf-8 characters and restrict the length
    text=text.decode('utf-8','ignore').encode("utf-8")
    words = text.split()
    if len(words) > MAX_LEN:
        words = words[:MAX_LEN]
    
    #Remove stopwords and stem
    ps = PorterStemmer()
    filtered_words = [word for word in words if word not in stopwords.words('english')]
    stemmed_words = [ps.stem(word) for word in filtered_words]
    lower_words = [word.lower() for word in stemmed_words]
    text = ' '.join(stemmed_words)

    return text

# Load the model
print "Loading the model"
model = fasttext.load_model(trained_model)
print "Model loaded"
title_row = ['rectype', 'sha', 'ins_del_count', 'issueid', 'actor', 'date', 'text', 'similarity']

# Gets the aggregated word vector representation of the text
def GetTextVector(text):
    final_vector = np.zeros((300,))
    words = text.split(' ')
    for word in words:
        if len(word) > CHAR_THRESHOLD:
            continue
        word_vector = model.get_word_vector(word)
        final_vector = final_vector + word_vector
    final_vector = final_vector/float(len(words))
    return final_vector


for filename in os.listdir(bursty_issues_dir):
    parts = filename.split('_burst_')
    project = parts[0]
    data = pd.read_csv(os.path.join(bursty_issues_dir, filename))
    output_filename = filename.replace('_issues.csv', '_mod_requests.csv')
    output_file = open(os.path.join(output_dir, output_filename), 'wb')
    # if(os.path.isfile(os.path.join(output_dir, output_filename)) == True):
    #     continue
    print "Processing for file: ", filename

    # Get all the PR commits in the burst
    pr_commits = data.loc[data['rectype'] == 'pull_request_commit']
    if(pr_commits.empty):
        print "No commits found in the issues in this burst. Skipping for file: ", filename
        continue

    # For each commit filter the commits that occur after the issue start
    after_issue_start = []
    for idx,row in pr_commits.iterrows():
        issue_id = row['issueid']
        issue_filter = data.loc[data['issueid'] == issue_id]
        issue_filter = issue_filter.loc[issue_filter['action'] == 'start issue']
        if(issue_filter.empty):
            # Issue must have started in another earlier burst
            after_issue_start.append(row)
            continue
        start_time = list(issue_filter['time'])[0]
        commit_time = row['time']
        if(commit_time >= start_time):
            after_issue_start.append(row)

    if(len(after_issue_start) == 0):
        print "No commit found that occured after issue start. Skiping for file: ", filename
        continue

    # Get the insertion deletion counts for each PR and retain the ones with counts >= 30
    high_impact_commits = []
    ins_del_file = os.path.join(ins_del_count_dir, project + '_ins_del_counts.pickle')
    ins_del_dir = pickle.load(open(ins_del_file, 'rb'))
    raw_commit_file = os.path.join(raw_commit_dir, 'repo_' + project.replace('~', '_', 1) + '_commits.csv')
    commit_data = pd.read_csv(raw_commit_file)
    for commit in after_issue_start:
        sha = commit['action']
        if(len(sha) == 0):
            continue
        counts = {}
        if sha in ins_del_dir:
            counts = ins_del_dir[sha]
        else:
            temp_commit = commit_data.loc[commit_data['text'] == commit['text']]
            if(temp_commit.empty):
                continue
            t_sha = list(temp_commit['action'])[0]
            if(t_sha not in ins_del_dir):
                continue
            counts = ins_del_dir[t_sha]
        total_count = counts['insert'] + counts['delete']
        commit['count'] = total_count
        if(total_count >= 30):
            high_impact_commits.append(commit)

    if(len(high_impact_commits) == 0):
        print "No high impact commit found in this burst. Skipping for file: ", filename

    # For the filtered PR get the comments in the corresponding issue that occur before the commit start.
    writer = csv.writer(output_file)
    writer.writerow(title_row)
    for commit in high_impact_commits:
        issue_id = commit['issueid']
        issue_filter = data.loc[data['issueid'] == issue_id]
        issue_filter = issue_filter[issue_filter['rectype'].str.contains('comment')]
        if(issue_filter.empty):
            continue
        commit_time = commit['time']
        issue_filter = issue_filter[issue_filter['time'] <= commit_time]
        if(issue_filter.empty):
            continue
        # For the found comments compute the agg. word vectors and the similarity score
        clean_text = CleanIssueComment(str(commit['text']))
        commit_vector = GetTextVector(str(clean_text))
        sim_scores = []
        for idx,row in issue_filter.iterrows():
            cleaned = CleanIssueComment(str(row['text']))
            comment_vector = GetTextVector(str(cleaned))
            sim = spatial.distance.cosine(commit_vector, comment_vector)
            sim_scores.append(sim)
            issue_filter.loc[idx, 'score'] = sim
        percentile = np.percentile(sim_scores, 70)
        num = issue_filter.shape[0]
        if num > 10:
            similar_comments = issue_filter[issue_filter['score'] >= percentile]
        else:
            similar_comments = issue_filter

        if similar_comments.empty:
            continue
        similar_comments.sort_values(by='score', ascending=False, inplace=True)
        # Write the output csv with the top comments per commit ['rectype', 'sha', 'ins_del_count', 'issueid', 'actor', 'date', 'text', 'similarity']
        writer.writerow([commit['rectype'], commit['action'], commit['count'], commit['issueid'], commit['actor'], commit['time'], commit['text'], "NA"])
        for idx,comment in similar_comments.iterrows():
            to_write = [comment['rectype'], "NA", "NA", comment['issueid'], comment['actor'], comment['time'], comment['text'], comment['score']]
            writer.writerow(to_write)
        writer.writerow([' ']*len(title_row))
        writer.writerow([' ']*len(title_row))
    output_file.close()



