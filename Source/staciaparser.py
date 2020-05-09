from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pymysql
import re

def parse(query):
    variables = get_vars(query)
    variables = coursename_to_id(variables)
    return variables

def add_varnames(query, variables):
    changed_query = query
    for input in variables:
        changed_query = re.sub(input[1], input[0], changed_query)
    return changed_query

# given an array of variables, changes all course ids to courrse names
def courseid_to_name(variables):
    connection = pymysql.connect(host='localhost',
                                 user='pglucas466',
                                 password='pglucasdb466',
                                 db='pglucas466',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            for var in variables:
                if var[0] == '[Course]':
                    command = 'SELECT department, code FROM course WHERE id = ' + str(var[1]) + ';'
                    cursor.execute(command)
                    coursename = cursor.fetchone()
                    var[1] = str(coursename['department']) + ' ' + str(coursename['code'])
        connection.commit()
    finally:
        connection.close()  
    return variables

# given an array of variables, changes all course names to course ids
def coursename_to_id(variables):
    for var in variables:
        if var[0] == '[Course]':
            var[1] = get_course_id(var[1])
    return variables

# given a question, finds all the variable references in the question
def get_vars(query):
    var_regex = var_features()
    input_variables = []
    for var in var_regex:
        variables = re.compile(var[1]).findall(query)
        if len(variables) > 0:
            if len(variables) > 1:
                if var[0] == '[Course]':
                    start_ind = re.search('prerequisites* for|before').span()[1]
                    pattern = re.compile(var[1])
                    input_variables.append([var_regex[0], pattern.findall(query[start_ind:])[0]])
                else:
                    for j in range(0, len(variables)):
                        input_variables.append([var[0], variables[j]])
            else:
                input_variables.append([var[0], variables[0]])
    for i in input_variables:
        if isinstance(i[1],tuple):
            for j in i[1]:
                if len(j)>0:
                    i[1] = str(j)
    return input_variables


# iterates through var_features.txt file and gets regex variable associations
def var_features():
    q_vars = []
    form = '(?P<variable>.+) : (?P<regex>.+)'
    with open('var_features.txt') as file:
        for line in file:
            m = re.match(form, line)
            if m != None:
                q_vars.append([m.group('variable'), m.group('regex')])
    return q_vars

# returns name of chatbot relevant to question or mark as irrelevant if there is none
# needs work to determine area
def check_relevance(query):
    csse_terms = ['CSC', 'SE', 'Computer Science', 'Software Engineering']
    stats_terms = ['STAT', 'Statistics']
    if any(term in query for term in csse_terms):
        department = 'CSSE'
    elif any(term in query for term in stats_terms):
        department = 'STAT'
    else:
        return 'irrelevant'
    return department


# given a course name and a database connection, gets the corresponding course id
def get_course_id(str):
    connection = pymysql.connect(host='localhost',
                                 user='pglucas466',
                                 password='pglucasdb466',
                                 db='pglucas466',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            course = str.split()
            dept = course[0]
            code = course[1]
            cursor = connection.cursor()
            command = 'SELECT id FROM course WHERE department = "{}" AND code = {};'
            command = command.format(dept, code)
            cursor.execute(command)
            output = cursor.fetchone()['id']
        connection.commit()
    finally:
        connection.close()  
    return output

# given answer format, variables, and sql query result, fully formatted answer
def format_answer(format, variables, result):
    answer = format
    for var in variables:
        answer = answer.replace(var[0], var[1], 1)
    result_str = ""
    for row in result:
        result_str =  row + ', '
    result_str = result_str[:-2]
    answer = re.sub('\[.+\]', result_str, answer)
    return answer

# given variable list and answer format, fetches information and puts it in the format
def final_answer(variables, answer):
    result = query(variables)
    variables = courseid_to_name(variables)
    answer = get_answer_format(label)
    answer_str = format_answer(answer, variables, result)
    return answer_str
