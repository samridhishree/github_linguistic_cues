'''
Reads the clean readme project texts and aggregates their word vectors.
Doesnt include words whose length exceeds threshold.
'''
import fastText.FastText as fasttext
import os
import sys
import numpy as np
from collections import defaultdict
import cPickle as pickle


CHAR_THRESHOLD = 25
readme_text_dir = sys.argv[1]
trained_model = sys.argv[2]
output_file = sys.argv[3]
index_file = sys.argv[4]

# Load the model
model = fasttext.load_model(trained_model)
project_index = defaultdict(lambda: len(project_index))
project_vectors = []

# Read each project readme and aggregate their word vectors
for filename in os.listdir(readme_text_dir):
    if '.txt' not in filename:
        continue
    print "Processing for = ", filename
    f = open(os.path.join(readme_text_dir, filename), 'rb')

    # Aggregate the word vectors from the file
    cur_vector = np.zeros((300,))
    for line in f:
        words = line.split(" ")
        for word in words:
            if len(word) > CHAR_THRESHOLD:
                print "Word too long = ", word
                continue
            word_vector = model.get_word_vector(word)
            cur_vector = cur_vector + word_vector
    project_vectors.append(cur_vector)
    project_name = filename.split('_readme_clean.txt')[0]
    project_index[project_name]

# Convert the list of vectors to ndarray
project_vectors = np.array(project_vectors)
print "Saving the matrix"
np.save(output_file, project_vectors)

print "Saving the project index"
pickle.dump(dict(project_index), open(index_file, 'w'))





