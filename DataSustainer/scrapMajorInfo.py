# scrapMajor: scrapes stats major info
# by Kevin Sanchez/ Spring 2019

import os, sys, random, requests, re
from bs4 import BeautifulSoup

def get_major_info():
    #obtain the content of the URL in HTML
    url = "http://catalog.calpoly.edu/collegesandprograms/collegeofsciencemathematics/statistics/bsstatistics/"
    myRequest = requests.get(url)

    #Create a soup object that parses the HTML
    soup = BeautifulSoup(myRequest.text,"html.parser")

    major_info = dict()

    # get the first 4 requirements
    upper_div_str = re.search('(\d+) units of upper division', soup.getText())
    upper_div_units = int(upper_div_str.group(1))
    major_info.update({'upper_div_units':upper_div_units})
    #print(upper_div_units)
    gwr_str = re.search('Graduation Writing Requirement (.+) ', soup.getText())
    gwr = gwr_str.group(1)[1:4]
    major_info.update({'gwr_req':gwr})
    #print(gwr)
    gpa_req_str = re.search('(\d+\.\d+) GPA', soup.getText())
    gpa_req = gpa_req_str.group(1)
    major_info.update({'gpa_req':gpa_req})
    #print(gpa_req)
    uscp_req_str = re.search('U.S. Cultural Pluralism (.+) ', soup.getText())
    uscp_req = uscp_req_str.group(1)[1:5]
    major_info.update({'uscp_req':uscp_req})
    #print(uscp_req)

    
    # all_courses to store lists of courses, each list is a level
    all_major_courses = {}
    
    index = 1
    for table in soup.find('table',attrs={'class':'sc_courselist'}):
        req_major_courses = {}
        elect_a_maj_courses = {}
        elect_b_maj_courses = {}
        supp_courses = {}
        for major_courses in table.find_all('td', attrs={'class':'codecol'}):
                course = major_courses.find('a').getText()
                maj_course_units = 0
                #for col in table.find_all('tr', attrs={'class':['odd','even']}):
                if index > 0 and index <= 20:
                    major_course = course
                    #maj_units_str = re.search('class="hourscol">(\d+)<', table.find())
                    #print(major_course)
                    req_major_courses[index] = {'course': major_course}
                    index += 1
                elif index > 20 and index < 31:
                    elect_a_major_course = course
                    #print(sup_a_major_course)
                    elect_a_maj_courses[index-20] = elect_a_major_course
                    index += 1
                elif index > 30 and index < 51:
                    elect_b_major_course = course
                    #print(sup_b_major_course)
                    elect_b_maj_courses[index-30] = elect_b_major_course
                    index += 1
                elif index > 50:
                    supp_courses[index-50] = course
                    index += 1
        major_info.update({'req_maj_courses':req_major_courses})
        major_info.update({'list_a_electives':elect_a_maj_courses})
        major_info.update({'list_b_electives':elect_b_maj_courses})
        major_info.update({'supp_course':supp_courses})
    ge_areas = {}
    ge_index = 0
    first_sec = 0
    for ge_area in soup.find_all('table', attrs={'class':'sc_courselist'}):
        # skip first table
        if first_sec == 0:
            first_sec += 1
            continue
        else:
            for ge_info in ge_area.find_all('span', attrs={'class':'courselistcomment areaheader'}):
                    if ge_index % 2 is 0:
                        ge_area = ge_info.getText()
                        ge_index += 1
                    else:
                        ge_title = ge_info.getText()
                        ge_areas[ge_index] = {'ge_area': ge_area, 'ge_title': ge_title}
                        ge_index += 1
    major_info.update({'ge_areas':ge_areas})
    #get units
    units = {}
    units_index = 0
    row_index = 1
    total_maj_units = 0
    maj_units_only = 0
    elec_a_units = 0
    elec_b_units = 0
    supp_units = 0
    for maj_units in soup.find_all('td', attrs={'class':'hourscol'}):
        # skip empty hours col
        tmp_units = maj_units.find(text=True)
        if tmp_units is None or int(tmp_units) == 0:
            row_index += 1
            continue
        elif int(tmp_units) == 180:
            break
        else:
            total_maj_units += int(tmp_units)
            if row_index >= 1 and row_index <= 22:
                maj_units_only += int(tmp_units)
            if int(tmp_units) == 64:
                ge_units = int(tmp_units)
            if row_index == 23:
                elec_a_units = int(tmp_units)
            elif row_index == 34:
                elec_b_units = int(tmp_units)
            elif row_index >= 57 and row_index <= 61:
                supp_units += int(tmp_units)
            row_index += 1
            #print(total_maj_units)
    free_elec = total_maj_units - elec_a_units - elec_b_units - supp_units - ge_units - maj_units_only
    units.update({'total_maj_units':total_maj_units,'maj_only_units':maj_units_only,'elec_a_units':elec_a_units,'elec_b_units':elec_b_units, 'supp_units': supp_units, 'ge_units':ge_units, 'free_elect':free_elec})
    major_info.update(units)
    
    return major_info

def main():
    print(get_major_info())
    #get_courses_lvl()

if __name__ == '__main__':
    main();
