# University Chatbot

## Scope
Development of a complete chatbot able to answer questions about statistics major, minor and curricula at California Polytechnic States University.

## Libraries & Tools
- NLTK | Wordnet | scikit-learn | BeautifulSoup | Regex | SQL

## Database
The database used to train the classifier was homemade: 
- 150 questions
- 25 labelled answers

## Bot Architecture & Workflow
#### 1) Data Sustainer
- Scrap several websites to get the data and store them.

#### 2) User interface
- Get the question from the user and return the answer.
  - *Example: What are the classes in junior year required by stats department as a stats major?*
  
#### 3) Parser
- Parse the question to extract the words of interest and normalize it.
  - *Example - Parsing: junior > junior, stats > statistics, stats major > statisitcs major* 
  
#### 4) Feature extractor & Classifier
- Classify the words of interest
  - *Example - Classification: junior > [Year name], statistics > [Department],  major > [Degree]*

- Extract the features from the question and classify it. The label correspond to a specific answer model associated to an SQL query.
  - *Example - Generic question classified: What are the [Year name] classes required by [Department] as [Degree]?  > labelled as 2*
 
#### 5) Answer builder
- Fill the SQL query with the words of interests and get the data.
  - *Example - Query:* 
    - *SELECT c.department,c.code,c.title FROM course AS c JOIN degree_courses AS dc ON c.id = dc.course JOIN degree AS d ON dc.degree = d.id WHERE  location1 = var1 AND location2 = var2 AND location3 = var3 ;*
    - *location1 = c.year, var1 = junior | location2 = c.department, var2 = statistics | location3 = dc.degree, var3 = statistics major*
    - *STATS, 101, Introduction to stats | STATS, 112, Linear Regressions*

- Get the labelled answer and fill it both with words of interests and answer data.
  - *Example - Answer model: As a [Degree], the following courses are required from [Department] in [Year Name]:[Course].*
  - *Example - Filled Answer: As a statistics major, the following courses are required from statistics department in junior year: STATS-101: Introduction to stats, STATS-112, Linear Regressions*

## Classifying results
Accuracy: 67% 
