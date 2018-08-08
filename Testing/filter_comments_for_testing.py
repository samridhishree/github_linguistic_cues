'''
Filters the comments strings from the clean and stemmed issues to get those associated with the tag "Testing"
'''

import os
import sys
import csv
import pandas as pd
from nltk.stem import PorterStemmer

reload(sys)
sys.setdefaultencoding('utf-8')

clean_issue_dir = sys.argv[1]
output_dir = sys.argv[2]

# Get the stemmed versions of all the keywords to search
keywords = ['test', 'coveralls', 'travis', 'codecov-io', 'travisci']
ps = PorterStemmer()
keywords = [ps.stem(word) for word in keywords]

# Process and filter each file one by one
for filename in os.listdir(clean_issue_dir):
    print "Processing for file: ", filename
    data = pd.read_csv(os.path.join(clean_issue_dir, filename))
    df = data.dropna(subset = ['clean_text'])
    df = df[df['rectype'].str.contains("comment")]
    clean_text = list(df['clean_text'])
    clean_text = [str(x) for x in clean_text]
    test_strings = [x for x in clean_text if any(word in x for word in keywords)]

    test_strings = []
    for text in clean_text:
        text = str(text)
        words = text.split()
        if any(word in words for word in keywords):
            test_strings.append(text)


    if len(test_strings) == 0:
        print "No test related strings found. Skipping."
        continue

    output_filename = filename.split('_clean.csv')[0] + '_test_filtered.csv'
    f = open(os.path.join(output_dir, output_filename), 'wb')
    writer = csv.writer(f)
    title_row = list(data.columns)
    title_row.append('Test')
    writer.writerow(title_row)

    # Write yes for test field, if the current row has one of the test strings
    for idx,row in data.iterrows():
        to_write = list(row)
        if (str(row['clean_text']) in test_strings) and ('comment' in row['rectype']):
            to_write.append("Y")
        else:
            to_write.append("N")
        writer.writerow(to_write)

    f.close()


