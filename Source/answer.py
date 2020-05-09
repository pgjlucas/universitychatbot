import pymysql.cursors
import csv
import os
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import re
from classifier import classifier
from staciaparser import parse,courseid_to_name
#from answer import get_answer
test = [['[Department]','STAT'],['[Fulfills]','required']]

def get_answer(question):
	fill_queries('sql_query.txt')
	parser_output = parse(question)
	print('Parser_output: ',parser_output)
	parameters = get_query_parameters(parser_output)
	print('Pararameters: ',parameters)
	question_format = reformulate_question(question,parser_output)
	print('Question Format: ',question_format)
	predict_label = classifier(question_format)
	print('Predict Label: ',predict_label)
	valid = check_parameters(parser_output,predict_label)
	print('Valid: ',valid)
	if valid == 10:
		parser_output = courseid_to_name(parser_output)
		answer_format = get_answer_format(parser_output,predict_label)
		print('Answer: ',answer_format)
		if answer_format == 0:
			return 'Could you reformulate the question?'
		else:
			output= query(parameters,predict_label)
			print('output: ',output)
			return get_answer_filled(answer_format,output)
	elif valid == False:
		return 'Could you reformulate the question?'
	else:
		return 'Could you be more precise? It seems that '+str(valid)+' arguments are missing.'
	return 'Could you reformulate the question'

def get_answer_format(parser_output,label):
	connection = pymysql.connect(host='localhost',
		                         user='pglucas466',
		                         password='pglucasdb466',
		                         db='pglucas466',
		                         charset='utf8mb4',
		                         cursorclass=pymysql.cursors.DictCursor)
	try:
		with connection.cursor() as cursor:
			query = 'SELECT answer FROM questions WHERE label =' + str(label) +';'
			cursor.execute(query)
			answers = cursor.fetchall()
		connection.commit()
	finally:
		connection.close()
	# Select the answer with the right variables > easier
	for a in answers:
		count = 0
		answer_format = a['answer']
		for p in parser_output:
			print("p",p)
			if p[0] in a['answer']:
				answer_format = answer_format.replace(p[0],p[1])
				print("p(0)",p[0])
				count = count + 1	
		print(count)	
		if count == len(parser_output):
			return answer_format
	return 0

def get_answer_filled(answer_format,output):
	str_output = output[0]
	if len(output)>1:
		for i in output:
			str_output = str_output + ', '+ i
	answer = re.sub('\[.+\]', str_output, answer_format)
	return answer


def reformulate_question(question,parser_output):
	for p in parser_output:
		if isinstance(p[0],str) and isinstance(p[1],str):
			question = question.replace(p[1], p[0])
		return question

def get_query_parameters(parser_output):
	bracket_list = {'[Requirement]':['d','requirements'],'[Course]':['c','id'],'[Grad_vs_Undergrad]':['c','grad'],'[Upper_vs_Lower]':['c','division'],'[Level Number]':['c','level'],'[Fulfills]':['dc','fulfills'],'[Department]':['c','department'],'[Quarter]':['c','quarters'],'[GPA]':['d','gpa'],'[Degree]':['d','programname']}
	parameters = []
	for bracket in parser_output:
		t_target = bracket_list[bracket[0]][0]
		c_target = bracket_list[bracket[0]][1]
		v_target = bracket[1]
		# Define target location in DB
		l_target = t_target + '.' + c_target
		parameters.append([l_target,v_target])
	return parameters

def fill_queries(file):
	connection = pymysql.connect(host='localhost',
		                         user='pglucas466',
		                         password='pglucasdb466',
		                         db='pglucas466',
		                         charset='utf8mb4',
		                         cursorclass=pymysql.cursors.DictCursor)
	try:
		with connection.cursor() as cursor:
			cursor.execute('DROP TABLE IF EXISTS queries;')
			cursor.execute('CREATE TABLE queries(label INTEGER, query VARCHAR(255), numparameters INTEGER, parameters VARCHAR(255));')
			sql_insert = "INSERT INTO queries (label, query, numparameters, parameters) VALUES (%s, %s, %s, %s);"
			with open(file,'r') as f:
				reader=csv.reader(f,delimiter='|')
				for line in reader:	
					if len(line)==4:
						label = line[0]
						query = line[1]		
						numparameters = line[2]
						parameters = line[3]				
						cursor.execute(sql_insert, (label, query, numparameters, parameters))
		connection.commit()
	finally:
		connection.close()

def check_parameters(parser_output,label):
	typeparameters = []
	connection = pymysql.connect(host='localhost',
		                         user='pglucas466',
		                         password='pglucasdb466',
		                         db='pglucas466',
		                         charset='utf8mb4',
		                         cursorclass=pymysql.cursors.DictCursor)
	try:
		with connection.cursor() as cursor:
			query = 'SELECT numparameters FROM queries WHERE label = %s ;'
			cursor.execute(query,str(label))
			numparameters = cursor.fetchall()
			query2 = 'SELECT parameters FROM queries WHERE label = %s ;'			
			cursor.execute(query2,str(label))
			resultparameters = cursor.fetchall()
		connection.commit()
	finally:
		connection.close()
	numparameters = numparameters[0]['numparameters']
	typeparameters = resultparameters[0]['parameters']
	typeparameters = typeparameters.split(',')
	if len(parser_output) == numparameters:
		count = 0
		for p in parser_output:
			if p[0] in typeparameters:
				count=count+1
		if count == numparameters:
			return 10 # The query is gonna work
		else:
			return False # Could you reformulate the questions ?()
	else:
		return numparameters - len(parser_output) # Could you be more precise (arguments missings)

def query(parameters,label):
	count = 1
	output =[]
	connection = pymysql.connect(host='localhost',
		                         user='pglucas466',
		                         password='pglucasdb466',
		                         db='pglucas466',
		                         charset='utf8mb4',
		                         cursorclass=pymysql.cursors.DictCursor)
	try:
		with connection.cursor() as cursor:
			cursor.execute('SELECT query FROM queries WHERE label =' + str(label) + ";")
			query = cursor.fetchone()
			query = query['query']
			for p in parameters:
				query = query.replace('location'+str(count),str(p[0]))
				query = query.replace('var'+str(count),"'"+str(p[1])+"'")
				count = count +1
			print(query)
			cursor.execute(query)
			result_variables = cursor.fetchall()
		connection.commit()
	finally:
		connection.close()
	# Process sql output
	for element in result_variables:
		answer  = ""
		for key,value in element.items():
			answer = answer + ' '+ str(value)
		output.append(answer)
	return output
