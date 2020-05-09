# scrapCoursesInfo: scrapes course info for stats/data courses
# by Kevin Sanchez/ Spring 2019

import os, sys, random, requests, re
from bs4 import BeautifulSoup

def get_courses_info():
    #obtain the content of the URL in HTML
    url = "http://catalog.calpoly.edu/collegesandprograms/collegeofsciencemathematics/statistics/#courseinventory"
    myRequest = requests.get(url)

    #Create a soup object that parses the HTML
    soup = BeautifulSoup(myRequest.text,"html.parser")
    
    # all_courses to store lists of courses, each list is a level
    all_courses = {}
    
    for courses in soup.find_all('div', attrs={'class':'courses'}):
        # lvl_courses holds all courses for certain level
        
        for course_info in courses.find_all('div', attrs={'class':'courseblock'}):
            # get full name of course
            name = course_info.find('p', attrs={'class':'courseblocktitle'}).find(text=True).strip()
            # dept and code
            course = name[0:8]
            # extract department
            department = name[0:4]
            #print(department)
            # extract code from course name
            code = int(name[5:8])
            #print(code)
            # extract course title
            title = name[10:]
            #print(title)
            # extract number of units
            unitsStr = course_info.find('span', attrs={'class':'courseblockhours'}).find(text=True).strip()
            
            if unitsStr[1:2] is '-':
                units = int(unitsStr[2:3])
            else:
                units = int(unitsStr[0:2])
            #print(units)
            course_offered = course_info.find('div', attrs={'class':'noindent courseextendedwrap'})
            cells = course_offered.findAll('p')
            gearea = None
            if len(cells) == 3:
                # check for GE area
                tmp = cells[0].find(text=True).split()
                if tmp[0] == 'GE':
                    gearea = tmp[2]
                elif tmp == 'CR/NC':
                    continue
                # get quarters when course is offered
                quarter = cells[1].getText()
                # get prereqs
                prerequisites = cells[2].getText()
            if len(cells) == 2:
                # get quarters when course is offered
                quarter = cells[0].getText()
                # get prereqs
                prerequisites = cells[1].getText()
            
            course_desc = course_info.find('div', attrs={'courseblockdesc'})
            #print(course_desc.find('p').getText())
            # get # of lectures
            lecturesStr = re.search('(\d+) lectures', course_desc.getText())
            if lecturesStr is not None:
                lectures = lecturesStr.group(1)
                #print(lectures)
            # get # of labs
            labsStr = re.search('(\d+) lab', course_desc.getText())
            if labsStr is not None:
                labs = int(labsStr.group(1))
                #print(labs)
            #print(code)
            all_courses[course] = {'depart': department, 'code': code, 'title': title, 'units': units, 'lecs': lectures, 'labs': labs, 'qtr': quarter, 'ge': gearea, 'prereq': prerequisites}
    return all_courses

def main():
    print(get_courses_info())
    #get_courses_lvl()

if __name__ == '__main__':
    main();