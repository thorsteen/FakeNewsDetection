from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
import psycopg2
import nltk
import pandas as pd


#cleaned database data
#data = pd.read_csv("article_entity.csv", skip_blank_lines=False, verbose = True, na_filter=False, names = ['content','type_id'], usecols = [1,3??])

#a sql call would be better
conn = psycopg2.connect(database='fknew', user='tsl19', password='0312', host='localhost', port="5432")

clean_query = pd.read_sql_query(
'''
SELECT content, type_id
FROM article
LIMIT 100000;
''',
conn)

content_type = pd.DataFrame(clean_query, columns=['content','type_id'])

conn.close()
print("read data")
content = content_type.loc[:,'content'].astype(str)


#make labels binary, either fake or not fake
def binLabels(liste):
    labels = []
    for i in liste:
        #if i == 'fake' #prediction on News sample and clean-100k made with i = 'fake' = 0 and all others 1
        if int(i) in [7,8,10]:
            labels.append(1)
        else:
            labels.append(0)
    return labels



#labels = binLabels(data['type'])
labels = binLabels(content_type['type_id'])
print("made labels")
articles = []

for i in range(len(content)):
    tokens = nltk.word_tokenize(content[i])
    lower_tokens = [t.lower() for t in tokens]
    alpha_only = [t for t in lower_tokens if t.isalpha()]
    articles.append(alpha_only)
print("tokenized article content")


"""
We need to format our tfidf and labels (might be an idea to pickle aslo)
"""

tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7)

X_train, X_test, y_train, y_test = train_test_split(content, labels, test_size=0.33) #maybe should specify a random state

tfidf_train = tfidf_vectorizer.fit_transform(X_train)

tfidf_test = tfidf_vectorizer.transform(X_test)

"""
we begin predicitnig with a linear SVM
"""
SVC_clf = LinearSVC(random_state=0)
print(SVC_clf.get_params(deep = True))
# Fit the classifier to the training data
SVC_clf.fit(tfidf_train, y_train)

# Create the predicted tags: pred
SVC_pred = SVC_clf.predict(tfidf_test)
print("predictions (0 = fake, 1 = not fake, from linear SVM classifier")
print(SVC_pred)

print("linear SVM classifier test accuracy score")
SVC_score = metrics.accuracy_score(y_test,SVC_pred)
print(SVC_score)

SVC_pred_train = SVC_clf.predict(tfidf_train)
SVC_score_train = metrics.accuracy_score(y_train,SVC_pred_train)
print("SVM train accuracy score")
print(SVC_score_train)


print("linear SVM classifier test confusion matrix")
cm1 = metrics.confusion_matrix(y_test, SVC_pred, labels=[0,1])
print(cm1)

"""
Then Naive Bayes for seconds
"""

# Instantiate a Multinomial Naive Bayes classifier: nb_classifier
nb_classifier = MultinomialNB()
print(nb_classifier.get_params(deep = True))
# Fit the classifier to the training data
nb_classifier.fit(tfidf_train, y_train)

# Create the predicted tags: pred
nb_pred = nb_classifier.predict(tfidf_test)
print("predictions (0 = fake, 1 = not fake, from naive bayes classifier")
print(nb_pred)

print("naive bayes classifier test accuracy score")
nb_score = metrics.accuracy_score(y_test,nb_pred)
print(nb_score)
nb_pred_train = nb_classifier.predict(tfidf_train)
nb_score_train = metrics.accuracy_score(y_train,nb_pred_train)
print("NB train accuracy score")
print(nb_score_train)

print("naive bayes classifier test confusion matrix")
cm2 = metrics.confusion_matrix(y_test, nb_pred, labels=[0,1])
print(cm2)

"""
We then use a K nearst neighboor classifier
"""
KNN_clf = KNeighborsClassifier(n_neighbors = 5, weights = "uniform" )
print(KNN_clf.get_params(deep = True))
KNN_clf.fit(tfidf_train, y_train)
KNN_pred = KNN_clf.predict(tfidf_test)

print("predictions (0 = fake, 1 = not fake, from a K nearst neighboor classifier")
print(KNN_pred)

print("K nearst neighboor classifier test accuracy score")
KNN_score = metrics.accuracy_score(y_test,KNN_pred)
print(KNN_score)
KNN_pred_train = KNN_clf.predict(tfidf_train)
KNN_score_train = metrics.accuracy_score(y_train,KNN_pred_train)
print("KNN train accuracy score")
print(KNN_score_train)

print(" K nearst neighboor classifier test confusion matrix")
cm3 = metrics.confusion_matrix(y_test, KNN_pred, labels=[0,1])
print(cm3)


"""
Lastly we try a Descision tree out
"""
tree_clf = DecisionTreeClassifier("gini")
print(tree_clf.get_params(deep = True))

# Fit the classifier to the training data
tree_clf.fit(tfidf_train, y_train)

# Create the predicted tags: pred
tree_pred_test = tree_clf.predict(tfidf_test)
print("predictions (0 = fake, 1 = not fake, from Descision tree callisifier")
print(tree_pred_test)

print("Descision tree test accuracy score")
tree_score_test = metrics.accuracy_score(y_test,tree_pred_test)
print(tree_score_test)

tree_pred_train = tree_clf.predict(tfidf_train)
tree_score_train = metrics.accuracy_score(y_train,tree_pred_train)
print("Descision tree train accuracy score")
print(tree_score_train)


print("Descision tree test confusion matrix")
cm4 = metrics.confusion_matrix(y_test, tree_pred_test, labels=[0,1])
print(cm4)

"""
Confusion matrix
[[TruePossitve   FalseNegative]
 [FalsePostive   TrueNegative ]]


results on News Sample
----------------------
Descision tree classifier has the best acc 93 pct.
Naive Bayes has the lowect acc with 62 pct.
""
results on clean-100k dataset
-----------------------
From best to worst
1.
Decision tree accuracy score
0.9762727272727273
Descision tree confusion matrix
[[14642   473]
 [  310 17575]]
2.
linear SVM classifier accuracy score
0.9757272727272728
linear SVM classifier confusion matrix
[[14435   680]
 [  121 17764]]
3.
naive bayes classifier accuracy score
0.8516969696969697
naive bayes classifier confusion matrix
[[11704  3411]
 [ 1483 16402]]
4.
K nearst neighboor classifier accuracy score
0.8131818181818182
 K nearst neighboor classifier confusion matrix
[[11593  3522]
 [ 2643 15242]]


results on 100k from fknew database
-----------------------
1.
Decision tree test accuracy score
0.9144848484848485
Descision tree train accuracy score
0.9997910447761194
Descision tree test confusion matrix
[[28451  1340]
 [ 1482  1727]]
2.
linear SVM classifier test accuracy score
0.9494848484848485
SVM train accuracy score
0.9951194029850746
linear SVM classifier test confusion matrix
[[29395   396]
 [ 1271  1938]]
3.
K nearst neighboor classifier test accuracy score
0.909060606060606
KNN train accuracy score
0.9222686567164179
 K nearst neighboor classifier test confusion matrix
[[29536   255]
 [ 2746   463]]
4.
naive bayes classifier test accuracy score
0.9067272727272727
NB train accuracy score
0.9081492537313433
naive bayes classifier test confusion matrix
[[29790     1]
 [ 3077   132]]

results are too high, might be because fake and not fake articles in dataset are unbalanced
"""
