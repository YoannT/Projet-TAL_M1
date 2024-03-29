#!/usr/bin/python
# -*-coding:Utf-8 -*

# Author: Olivier Grisel <olivier.grisel@ensta.org>
#		 Lars Buitinck <L.J.Buitinck@uva.nl>
#		 Chyi-Kwei Yau <chyikwei.yau@gmail.com>
# License: BSD 3 clause

from __future__ import print_function
from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups

import os
import codecs

n_samples = 2000
n_features = 1000
n_topics = 10
n_top_words = 20


def print_top_words(model, feature_names, n_top_words):
	for topic_idx, topic in enumerate(model.components_):
		print("Topic #%d:" % topic_idx)
		print(" ".join([feature_names[i]
		for i in topic.argsort()[:-n_top_words - 1:-1]]))
	print()


# Load the 20 newsgroups dataset and vectorize it. We use a few heuristics
# to filter out useless terms early on: the posts are stripped of headers,
# footers and quoted replies, and common English words, words occurring in
# only one document or in at least 95% of the documents are removed.

'''
print("Loading dataset...")
t0 = time()
dataset = fetch_20newsgroups(shuffle=True, random_state=1,
remove=('headers', 'footers', 'quotes'))
data_samples = dataset.data
print("done in %0.3fs." % (time() - t0))
print (len(data_samples))
'''

def replacemult(string,old,new):
	nstring = string

	for i in range(len(old)):
		nstring = nstring.replace(old[i],new[i])

	return nstring

def replaceAll(string):
	return replacemult(string,[u'é',u'è',u'ê',u'à',u'â',u'î',u'ï',u'ô',u'û',u'ù',u"'",u'-',u'ç',u'œ'],['e','e','e','a','a','i','i','o','u','u',' ',' ','c','oe'])

def lecturevoeux(path):
    res = []
    names = []
    listdir = os.listdir(path)
    for f in listdir:
        names.append(f)
        alltxts=''
        fic = codecs.open(path+f,'r','utf8')
        for ligne in fic:
            if ligne[0] == '\n':
                continue
            tmp = ligne.split('.')
            for tmp2 in tmp:
                if tmp2 == '\n':
                    break
                alltxts+=replaceAll(tmp2)
        res.append(alltxts)
    return res, names

path = "../data/VoeuxPresidents/"

data_samples,names = lecturevoeux(path)

# Use tf-idf features for NMF.
print("Extracting tf-idf features for NMF...")
tfidf_vectorizer = TfidfVectorizer(max_df=0.7, min_df=2, #max_features=n_features,
			 stop_words=None)
t0 = time()
tfidf = tfidf_vectorizer.fit_transform(data_samples)
print("done in %0.3fs." % (time() - t0))

# Use tf (raw term count) features for LDA.
print("Extracting tf features for LDA...")
tf_vectorizer = CountVectorizer(max_df=0.7, min_df=2, max_features=n_features,
stop_words=None)
t0 = time()
tf = tf_vectorizer.fit_transform(data_samples)
print("done in %0.3fs." % (time() - t0))

# Fit the NMF model
print("Fitting the NMF model with tf-idf features,"
		"n_samples=%d and n_features=%d..."
		% (n_samples, n_features))
t0 = time()
nmf = NMF(n_components=n_topics, random_state=1, alpha=.1, l1_ratio=.5).fit(tfidf)
#exit()
print("done in %0.3fs." % (time() - t0))

print("\nTopics in NMF model:")
tfidf_feature_names = tfidf_vectorizer.get_feature_names()
print_top_words(nmf, tfidf_feature_names, n_top_words)

print("Fitting LDA models with tf features, n_samples=%d and n_features=%d..."
		% (n_samples, n_features))
lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5,
		learning_method='online', learning_offset=50.,
		random_state=0)
t0 = time()
lda.fit(tf)
print("done in %0.3fs." % (time() - t0))

print("\nTopics in LDA model:")
tf_feature_names = tf_vectorizer.get_feature_names()
print_top_words(lda, tf_feature_names, n_top_words)
