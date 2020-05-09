# scrapMinorCourses: scrapes course info for stats minor courses
# by Kevin Sanchez/ Spring 2019

import os, sys, random, requests, re
from bs4 import BeautifulSoup

def get_minor_courses():
    #obtain the content of the URL in HTML
    url = "http://catalog.calpoly.edu/collegesandprograms/collegeofsciencemathematics/statistics/statisticsminor/"
    myRequest = requests.get(url)

    #Create a soup object that parses the HTML
    soup = BeautifulSoup(myRequest.text,"html.parser")
    # minor_info to store all major info
    minor_info = {}
    minor_index = 0
    # all_courses to store lists of courses, each list is a level
    all_minor_courses = dict()
    
    intro_units = int(soup.find('tr', attrs={'class':'even firstrow'}).find('td', attrs={'class':'hourscol'}).find(text=True))
    #print(intro_units)
    minor_info.update({'intro_units':intro_units})
    minor_index += 1
    total_units = int(soup.find('tr', attrs={'class':'listsum'}).find('td', attrs={'class':'hourscol'}).find(text=True))
    minor_info.update({'total_units':total_units})
    minor_index += 1
    #print(total_units)
    other_units = total_units - intro_units
    minor_info.update({'other_units':other_units})
    minor_index += 1
    #print(other_units)
    all_intro_series = {}
    other_minor_courses = {}
    index = 1
    for table in soup.find('table',attrs={'class':'sc_courselist'}):
        for minor_courses in table.find_all('td', attrs={'class':'codecol'}):
            if index <= 20:
                three_courses = minor_courses.find_all('a')
                intro_series = {}
                if len(three_courses) == 3:
                    intro_course1 = three_courses[0].getText()
                    intro_course2 = three_courses[1].getText()
                    intro_course3 = three_courses[2].getText()
                    intro_series = {'first_course':intro_course1, 'second_course':intro_course2, 'third_course':intro_course3}
                    #print(intro_series)
                all_intro_series[index] = intro_series
                index += 1
            else:
                min_course = minor_courses.find('a').getText()
                #print(min_course)
                other_minor_courses[index-20] = min_course
                index += 1
        minor_info.update({'intro_serires':all_intro_series})
        minor_index += 1
        #print(all_intro_series)
        minor_info.update({'other_courses':other_minor_courses})
        minor_index += 1
        #print(other_minor_courses)
    return minor_info

def main():
    print(get_minor_courses())
    #get_courses_lvl()

if __name__ == '__main__':
    main();