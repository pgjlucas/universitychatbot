import nltk
from nltk.corpus import udhr
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import pymysql.cursors
import csv
import os
from collections import Counter
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import random

def classifier(question):
	# parameters for tests : neighbors,param,estimators, max_sample,max_feature, depth
	# Fill database with questions
	fill_questions('query.txt')
	# Format the data from DB
	questions_labelled = get_data_from_db() 
	all_questions_features  = get_features_vector(questions_labelled)
	# Get the feature vector format
	all_features_vector = get_allFeatures_vector(all_questions_features)
	# Get the feature vector for each label 
	all_numeric_features_vectors = get_numeric_feature_vectors_training(all_questions_features,all_features_vector)
	# Train the model 
	X = all_numeric_features_vectors['values']
	Y = all_numeric_features_vectors['labels']
	# Train Part of the model
	'''
	accuracy_knn = 0
	accuracy_dtree = 0
	accuracy_bag_dtree = 0
	accuracy_bag_knn = 0
	accuracy_RF = 0
	DTree = DecisionTreeClassifier(random_state=0)
	neigh = KNeighborsClassifier(n_neighbors=neighbors, weights='distance', algorithm='auto',p=param,metric='minkowski')
	RF = RandomForestClassifier(n_estimators=estimators, max_depth=depth, random_state=0, bootstrap=True)
	Bagging_DTree = BaggingClassifier(base_estimator=DTree, n_estimators=estimators, max_samples=max_sample, max_features=max_feature)
	Bagging_neigh = BaggingClassifier(base_estimator=neigh, n_estimators=estimators, max_samples=max_sample, max_features=max_feature)
	#AdaB_neigh = AdaBoostClassifier(base_estimator=neigh, n_estimators=50, learning_rate=1.0, random_state=None)
	for i in range(20) :
		dataSplit = split_data_train_test(X,Y,0.8)
		X_train = dataSplit[0]
		Y_train = dataSplit[1]
		X_test = dataSplit[2]
		Y_test = dataSplit[3]
		neigh.fit(X_train, Y_train)	
		DTree.fit(X_train, Y_train)
		RF.fit(X_train, Y_train)
		Bagging_DTree.fit(X_train, Y_train)
		Bagging_neigh.fit(X_train, Y_train)
		accuracy_RF = accuracy_RF + RF.score(X_test, Y_test)
		accuracy_dtree = accuracy_dtree + DTree.score(X_test, Y_test)
		accuracy_knn = accuracy_knn + neigh.score(X_test, Y_test)
		accuracy_bag_dtree = accuracy_bag_dtree + Bagging_DTree.score(X_test, Y_test)
		accuracy_bag_knn = accuracy_bag_knn + Bagging_neigh.score(X_test, Y_test)
		#accuracy_ada_knn = accuracy_ada_knn + AdaB_neigh.score(X_test, Y_test)
	'''
	# Test part of the model
	print('Accuracy K-NN: ',accuracy_knn/20)
	print('Accuracy TREE: ',accuracy_dtree/20)
	print('Accuracy Bag_KNN:',accuracy_bag_knn/20)
	print('Accuracy Bag_Tree:',accuracy_bag_dtree/20)
	print('Accuracy RF: ', accuracy_RF/20)
	
	#Prediction part for final model
	clf = DecisionTreeClassifier(random_state=0)
	clf.fit(X, Y)
	predict_features = get_question_features(str(question))
	numeric_features_vector = get_numeric_feature_vectors_testing(predict_features,all_features_vector)
	numeric_features_vector = np.array(numeric_features_vector)
	numeric_features_vector.reshape(-1,1)
	label = clf.predict(numeric_features_vector)
	
	return label[0]


def fill_questions(file):
	connection = pymysql.connect(host='localhost',
		                         user='pglucas466',
		                         password='pglucasdb466',
		                         db='pglucas466',
		                         charset='utf8mb4',
		                         cursorclass=pymysql.cursors.DictCursor)
	try:
		with connection.cursor() as cursor:
			cursor.execute('DROP TABLE IF EXISTS questions;')
			cursor.execute('CREATE TABLE questions(team CHAR(2),question VARCHAR(255),answer VARCHAR(255),label INTEGER);')
			sql_insert = "INSERT INTO questions (team, question, answer, label) VALUES (%s, %s, %s, %s)"
			with open(file,'r') as f:
				#next(f) # skip headings
				reader=csv.reader(f,delimiter='|')
				for line in reader:	
					if len(line)==4:
						team = line[0]
						question = line[1]	
						answer = line[2]	
						label = line[3]							
						cursor.execute(sql_insert, (team, question, answer, label))
		connection.commit()
	finally:
		connection.close()	

def get_data_from_db():
	question_list = []
	label_list = []
	connection = pymysql.connect(host='localhost',
		                         user='pglucas466',
		                         password='pglucasdb466',
		                         db='pglucas466',
		                         charset='utf8mb4',
		                         cursorclass=pymysql.cursors.DictCursor)
	try:
		with connection.cursor() as cursor:
			# Drop & Create table
			sql_get1 = "SELECT question FROM questions;"
			sql_get2 = "SELECT label FROM questions;"
			cursor.execute(sql_get1)
			questions = cursor.fetchall()
			cursor.execute(sql_get2)
			labels = cursor.fetchall()
		connection.commit()
	finally:
		connection.close()
	for q in questions:
		for key,value in q.items():
			question_list.append(value)
	for l in labels:
		for key,value in l.items():
			label_list.append(value)
	# Sort data per label
	data = list(zip(question_list,label_list))
	sorted(data, key=lambda label: label[1])
	question_list, label_list = zip(*data)	
	return question_list,label_list

def split_data_train_test(questions,labels,ratio_train_test):
	dataSet = list(zip(questions,labels))
	random.shuffle(dataSet)
	questions, labels = zip(*dataSet)
	splitPoint = int(len(questions)*ratio_train_test)
	train_questions = questions[:splitPoint]
	train_labels = labels[:splitPoint]
	test_questions = questions[splitPoint:]
	test_labels = labels[splitPoint:]
	return train_questions,train_labels,test_questions,test_labels

def get_question_features(sent):
    features = []
    hyperWords =[]
    words = []
    rawWords = nltk.word_tokenize(sent)
    rawWords = [w.lower() for w in rawWords if w[0] not in "][-_!?;:\"\'.," and w.lower() not in stopwords.words('english')]               
    #rawWords = nltk.pos_tag(rawWords)
    for w in rawWords:
        if wn.synsets(w) and wn.synsets(w)[0].hypernyms():
            words.append(w)
            words.append(wn.synsets(w)[0].lemmas()[0].name())
            hyperWords.append(wn.synsets(w)[0].hypernyms()[0].lemmas()[0].name())
        elif not wn.synsets(w):
            words.append(w)
    features = words+hyperWords
    if features:
          return features

def get_features_vector(questions_labels):
	questions = questions_labels[0]
	labels = questions_labels[1]
	features_vector=[]
	for i in range(0,len(questions)):
		# Get the features for each question
		features_vector.append([get_question_features(questions[i]),labels[i]])
	return features_vector

def get_numeric_feature_vectors_training(features_per_label,all_features_vector):
	all_features_values = []
	all_features_labels = []
	features = {}
	# Go through each class and create the vector
	for q in features_per_label:
		features_vector_copy = all_features_vector.copy()
		numeric_vector = []
		# Go through each feature
		for f in q[0]:
			if f in all_features_vector:
				features_vector_copy[f] = 1
		# Convert to numeric vector
		for k,v in features_vector_copy.items():
			numeric_vector.append(v)
		all_features_labels.append(q[1])
		all_features_values.append(numeric_vector)
	features['values'] = np.array(all_features_values)
	features['labels'] = np.array(all_features_labels)
	return features

def get_numeric_feature_vectors_testing(features_vector,all_features_vector):
	numeric_vector = []
	features_vector_copy = all_features_vector.copy()
	for f in features_vector:
		if f in all_features_vector:
			features_vector_copy[f] = 1
	for k,v in features_vector_copy.items():
		numeric_vector.append(v)
	return numeric_vector

def get_allFeatures_vector(features_per_label):
	all_features_vector= {}
	for q in features_per_label:
		for f in q[0]:
			all_features_vector[str(f)]=0
	return all_features_vector
