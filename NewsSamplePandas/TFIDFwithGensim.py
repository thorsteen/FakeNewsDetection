# -*- coding: utf-8 -*-
"""
Created on Thu May  7 14:53:45 2020

@author: tsl19
"""


import pandas as pd
#from collections import Counter
from collections import defaultdict
from gensim.models.tfidfmodel import TfidfModel
from gensim.corpora.dictionary import Dictionary
#from nltk.stem import WordNetLemmatizer
#from nltk.corpus import stopwords
from sklearn.svm import LinearSVC
import nltk
import itertools
#from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

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
We need to format our tfidf and labels
"""

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

tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7)

X_train, X_test, y_train, y_test = train_test_split(data['content'], labels, test_size=0.33) #maybe should specify a random state

tfidf_train = tfidf_vectorizer.fit_transform(X_train)

tfidf_test = tfidf_vectorizer.transform(X_test)

print("the first 10 features")
print(tfidf_vectorizer.get_feature_names()[:10])
print("vectors")
print(tfidf_train.A[:5])


# We create the TfidfVectorizer DataFrame: tfidf_df
tfidf_df = pd.DataFrame(tfidf_train.A, columns=tfidf_vectorizer.get_feature_names())

print("head of tfidf_df")
print(tfidf_df.head())

"""
we begin predicitnig with a linear SVM
"""
SVC_clf = LinearSVC(random_state=0)

# Fit the classifier to the training data
SVC_clf.fit(tfidf_train, y_train)

# Create the predicted tags: pred
SVC_pred = SVC_clf.predict(tfidf_test)
print("predictions (0 = fake, 1 = not fake, from linear SVM classifier")
print(SVC_pred)

print("linear SVM classifier accuracy score")
SVC_score = metrics.accuracy_score(y_test,SVC_pred)
print(SVC_score)

print("linear SVM classifier confusion matrix")
cm1 = metrics.confusion_matrix(y_test, SVC_pred, labels=[0,1])
print(cm1)

"""
Then Naive Bayes for seconds
"""

# Instantiate a Multinomial Naive Bayes classifier: nb_classifier
nb_classifier = MultinomialNB()

# Fit the classifier to the training data
nb_classifier.fit(tfidf_train, y_train)

# Create the predicted tags: pred
nb_pred = nb_classifier.predict(tfidf_test)
print("predictions (0 = fake, 1 = not fake, from naive bayes classifier")
print(nb_pred)

print("naive bayes classifier accuracy score")
nb_score = metrics.accuracy_score(y_test,nb_pred)
print(nb_score)

print("naive bayes classifier confusion matrix")
cm2 = metrics.confusion_matrix(y_test, nb_pred, labels=[0,1])
print(cm2)

"""
We then use a K nearst neighboor classifier
"""
KNN_clf = KNeighborsClassifier(n_neighbors = 5, weights = "uniform" )

KNN_clf.fit(tfidf_train, y_train)
KNN_pred = KNN_clf.predict(tfidf_test)

print("predictions (0 = fake, 1 = not fake, from a K nearst neighboor classifier")
print(KNN_pred)

print("K nearst neighboor classifier accuracy score")
KNN_score = metrics.accuracy_score(y_test,KNN_pred)
print(KNN_score)

print(" K nearst neighboor classifier confusion matrix")
cm3 = metrics.confusion_matrix(y_test, KNN_pred, labels=[0,1])
print(cm3)


"""
Lastly we try a Descision tree out
"""
tree_clf = DecisionTreeClassifier("gini")

# Fit the classifier to the training data
tree_clf.fit(tfidf_train, y_train)

# Create the predicted tags: pred
tree_pred = tree_clf.predict(tfidf_test)
print("predictions (0 = fake, 1 = not fake, from Descision tree callisifier")
print(tree_pred)

print("Descision tree accuracy score")
tree_score = metrics.accuracy_score(y_test,tree_pred)
print(tree_score)

print("Descision tree confusion matrix")
cm4 = metrics.confusion_matrix(y_test, tree_pred, labels=[0,1])
print(cm4)

"""
results on News Sample
--------------
Descision tree classifier has the best acc 93 pct.
Naive Bayes has the lowect acc with 62 pct.

"""