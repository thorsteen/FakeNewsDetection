# -*- coding: utf-8 -*-
"""
Created on Thu May  7 14:53:45 2020

@author: tsl19
"""


import pandas as pd
from collections import Counter
from collections import defaultdict
from gensim.models.tfidfmodel import TfidfModel
from gensim.corpora.dictionary import Dictionary
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.svm import LinearSVC
import nltk
import itertools
#from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

filename ='news_sample.csv' #works with this data

"""
We read the data raw to calculate Tfidf Model
"""

data = pd.read_csv(filename, encoding='utf-8', skip_blank_lines=True, verbose = True, na_filter=True)

content  = data.loc[:,'content']

articles = []

for i in range(len(content)):
    tokens = nltk.word_tokenize(data.loc[i,'content'])
    lower_tokens = [t.lower() for t in tokens]
    alpha_only = [t for t in lower_tokens if t.isalpha()]
    articles.append(alpha_only)
    
"""
#this is how we tokenize ...

tokens = nltk.word_tokenize(data.loc[0,'content'])

english_stops = stopwords.words('english')

lower_tokens = [t.lower() for t in tokens]

alpha_only = [t for t in lower_tokens if t.isalpha()]

no_stops = [t for t in alpha_only if t not in english_stops]

wordnet_lemmatizer = WordNetLemmatizer()

lemmatized = [wordnet_lemmatizer.lemmatize(t) for t in no_stops]

# create a bag-of-words for fun
bow = Counter(lemmatized)
"""

"""
We begin by making corpus
"""

dictionary = Dictionary(articles)

corpus = [dictionary.doc2bow(article) for article in articles]
print(corpus[0][:10])

"""
We calculate IDF onthe first article
"""

# Save the fifth document: doc
doc = corpus[0]

# Sort the doc for frequency: bow_doc
bow_doc = sorted(doc, key=lambda w: w[1], reverse=True)

# Print the top 5 words of the document alongside the count
for word_id, word_count in bow_doc[:5]:
    print(dictionary.get(word_id), word_count)
    
# Create the defaultdict: total_word_count
total_word_count = defaultdict(int)

for word_id, word_count in itertools.chain.from_iterable(corpus):
    total_word_count[word_id] += word_count
    
# Create a sorted list from the defaultdict: sorted_word_count
sorted_word_count = sorted(total_word_count.items(), key=lambda w: w[1], reverse=True) 

# Print the top 5 words across all documents alongside the count
for word_id, word_count in sorted_word_count[:5]:
    print(dictionary.get(word_id), word_count)

# Create a new TfidfModel using the corpus: tfidf
tfidf = TfidfModel(corpus)

# Calculate the tfidf weights of doc: tfidf_weights
tfidf_weights = tfidf[doc]

# Sort the weights from highest to lowest: sorted_tfidf_weights
sorted_tfidf_weights = sorted(tfidf_weights, key=lambda w: w[1], reverse=True)

print("We have mad our model of all articles in data")
print(tfidf)
print("Top weights of the first article")

for term_id, weight in sorted_tfidf_weights[:10]:
    print(dictionary.get(term_id), weight)

"""
We try out prediction with sklearn SVM classifier on a train and test dataset from raw data


clf = LinearSVC(random_state=0)

#make labels binary, either fake or not fake
def binLabels(liste):
    labels = []
    for i in liste:
        if i == 'fake':
            labels.append(0)
        else:
            labels.append(1)
    return labels

labels = binLabels(data['type'])

X_train, X_test, y_train, y_test = train_test_split(corpus, labels, test_size=0.33)

need to format input properly
"""