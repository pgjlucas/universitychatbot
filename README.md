# University Chatbot

### Scope
Development of a complete chatbot able to answer questions about statistics major, minor and curricula at California Polytechnic States University.

### Libraries & Tools
• NLTK • Wordnet • scikit-learn • BeautifulSoup • Regex • SQL

### Bot Architecture
#### Data Sustainer
- Scrap several websites to get the data and store them.

#### User interface
- Get the questions from the user and return the answers.

*Example: What are the junior classes required by stats department as a major?*
#### Parser
- Parse the questions to extract the words of interest and normalize them.

*Example - Parsing: junior > junior, stats > statistics, major > major* 
#### Feature extractor & Classifier
- Classify the words of interest

*Example - Classification: junior > [Year name], statistics > [Department],  major > [Degree]*

- Extract the features from the questions and classify them. The labels correspond to a specific answer model.

*Example - Generic question classified: What are the [Year name] classes required by [Department] as [Degree]?  > labelled as 2*
 
#### Answer builder
- Get the answer data from the database with the labelled query filled with the words of Interests

*Example - Query:* 
- *location1 = c.year, var1 = junior | location2 = c.departlent, var2 = statistics | location3 = dc.degree, var3 = statistics*
- *SELECT c.department,c.code,c.title FROM course AS c JOIN degree_courses AS dc ON c.id = dc.course JOIN degree AS d ON dc.degree = d.id WHERE  location1 = var1 AND location2 = var2 AND location3 = var3 ;*
- *STATS, 101, Introduction to stats | STATS, 112, Linear Regressions*

- Get the labelled answer and fill it both with words of interests and answer data.

- *Example - Answer model: As a [Degree], the following courses are required from [Department] in [Year Name]:[Course].*
- *Example - Filled Answer: As a statistics major, the following courses are required from statistics department in junior year: STATS-101: Introduction to stats, STATS-112, Linear Regressions*

### Classifying results
Accuracy: 67% 
