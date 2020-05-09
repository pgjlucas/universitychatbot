# DataSustainer

import sys
import pymysql

# scraping functions
from scrapCoursesInfo import get_courses_info
from scrapCoursesLevels import get_courses_lvl
from scrapMajorInfo import get_major_info
from scrapMinorCourses import get_minor_courses

# return graduate, division and numerical levels 
# given a course code
def getLevelVariables(code):
    first = code[0]
    if first == '1':
        return "undergraduate", "lower", 100
    if first == '2':
        return "undergraduate", "lower", 200
    if first == '3':
        return "undergraduate", "upper", 300
    if first == '4':
        return "undergraduate", "upper", 400
    if first == '5':
        return "graduate", "upper", 500
    return None, None, None

# given a dictionary of dictionaries
# returns sequence that can be input into the db
def parseCourses(data):
    result = []
    for big_key, big_value in data.items():
        #quarter = big_value["qtr"].split(":")[1].replace(",","").replace(" ","")
        quarter = big_value["qtr"].split(":")[1].replace(" ","")
        prereqs = big_value["prereq"].replace("Prerequisite: ","").replace(".","")
        grad, div, level = getLevelVariables(str(big_value["code"]))
        title = big_value["title"].replace(".","")
        values = (big_value["depart"],big_value["code"],title,big_value["units"],
                    big_value["lecs"], big_value["labs"],quarter, big_value["ge"],prereqs,
                    grad, div, level)
        result.append(values)
    return result

# given a dictionary of dictionaries
# returns sequence that can be input into the db
def parseMinor(data):

    minor = ("STAT","Minor",data["total_units"],None,None,None,None,None,None,None)
    
    intro = []
    for big_key,big_value in data["intro_serires"].items():
        intro.append((big_key,big_value["first_course"],big_value["second_course"],big_value["third_course"]))

    course = []
    courses = []
    for key,value in data["other_courses"].items():
        course_name = value.split("\xa0")
        grad, div, level = getLevelVariables(str(course_name[1]))
        course.append((course_name[0],course_name[1],None,None,None,None,None,None,None,grad,div,level))
        courses.append((course_name[0],course_name[1]))

    return minor, intro, course, courses

# given a dictionary of dictionaries
# returns sequence that can be input into the db
def parseMajor(data):
    totalUnits = 180
    requiredUnits = 71
    electiveUnits = 24
    supportUnits = 16
    freeUnits = 5
    geUnits = 64
    req = data["gwr_req"] + ", " + data["uscp_req"]
    major = ("STAT","Major",totalUnits, requiredUnits, electiveUnits, supportUnits, 
                freeUnits, geUnits, req, int(data["gpa_req"][0]))
    
    req_courses = []
    for key,value in data["req_maj_courses"].items():
        course = value["course"].replace("/CPE","").split("\xa0")
        grad, div, level = getLevelVariables(str(course[1]))
        req_courses.append((course[0],course[1],None,None,None,None,None,None,None,grad,div,level))

    electives = []
    for key,value in data["list_a_electives"].items():
        if ("/CPE" in value):
            course = value.split("/CPE ")
        else:
            course = value.split("\xa0")
        grad, div, level = getLevelVariables(str(course[1]))
        electives.append((course[0],course[1],None,None,None,None,None,None,None,grad,div,level))

    for key,value in data["list_b_electives"].items():
        if ("/CPE" in value):
            course = value.split("/CPE ")
        else:
            course = value.split("\xa0")
        grad, div, level = getLevelVariables(str(course[1]))
        electives.append((course[0],course[1],None,None,None,None,None,None,None,grad,div,level))

    support = []
    for key,value in data["supp_course"].items():
        if ("/CPE" in value):
            course = value.split("/CPE ")
        else:
            course = value.split("\xa0")
        grad, div, level = getLevelVariables(str(course[1]))
        support.append((course[0],course[1],None,None,None,None,None,None,None,grad,div,level))

    ge = []
    for key,value in data["ge_areas"].items():
        ge.append((value["ge_area"],value["ge_title"]))

    return major, req_courses, electives, support, ge
        

# prints whatever the scraping program returns
def parseData(data):
    #for big_key, big_value in data.items():
        for key, value in data.items():
            print(key, ":", value)


def main():

    # PREPARED DROP TABLE STATEMENTS
    
    dropDegreeSQL = "DROP TABLE IF EXISTS degree;"
    dropCourseSQL = "DROP TABLE IF EXISTS course;"
    dropDegreeCourseSQL = "DROP TABLE IF EXISTS degree_courses;"
    #dropAltSQL = "DROP TABLE IF EXISTS alternatives;"
    dropIntroSQL = "DROP TABLE IF EXISTS introductory_sequences;"
    dropGESQL = "DROP TABLE IF EXISTS gearea;"
    dropTablesSQLList = [dropDegreeSQL, dropCourseSQL, dropDegreeCourseSQL, dropIntroSQL, dropGESQL]

    # PREPARED CREATE TABLE STATEMENTS
    createDegreeSQL = ("CREATE TABLE degree ("
                        "`id`                INTEGER AUTO_INCREMENT,"
                        "title               VARCHAR(6) NOT NULL,"
                        "programname         VARCHAR(50) NOT NULL,"
                        "totalunits          INTEGER NOT NULL,"
                        "requiredcourseunits INTEGER,"
                        "techelectiveunits   INTEGER,"
                        "supportcourseunits  INTEGER,"
                        "freeelectiveunits   INTEGER,"
                        "geunits             INTEGER,"
                        "requirements        VARCHAR(20),"
                        "gpa                 INTEGER,"
                        "PRIMARY KEY (id));"
                    )
    createCourseSQL = ("CREATE TABLE course ("
                        "`id`          INTEGER AUTO_INCREMENT,"
                        "department    CHAR(4) NOT NULL,"
                        "code          INTEGER NOT NULL,"
                        "title         VARCHAR(100),"
                        "units         INTEGER,"
                        "lectures      INTEGER,"
                        "labs          INTEGER,"
                        "quarters      CHAR(6),"
                        "gearea        CHAR(3),"
                        "prerequisites VARCHAR(150),"
                        "grad          VARCHAR(20),"
                        "division      VARCHAR(6),"
                        "level         INTEGER,"
                        "UNIQUE (department,code),"
                        'PRIMARY KEY (id));'
                    )
    createDegreeCourseSQL = ("CREATE TABLE degree_courses ("
                            "degree   INTEGER,"
                            "course   INTEGER,"
                            "fulfills VARCHAR(20),"
                            "PRIMARY KEY (degree,course,fulfills),"
                            "FOREIGN KEY (degree) "
                            "    REFERENCES degree(id)"
                            "    ON DELETE CASCADE,"
                            "FOREIGN KEY (course)" 
                            "    REFERENCES course(id)"
                            "    ON DELETE CASCADE);"
                        )
    '''
    createAltSQL = ("CREATE TABLE alternatives ("
                    "ogcourse    INTEGER,"
                    "alternative INTEGER,"
                    "PRIMARY KEY (ogcourse, alternative),"
                    "FOREIGN KEY (ogcourse) "
                    "    REFERENCES course(ID)"
                    "    ON DELETE CASCADE,"
                    "FOREIGN KEY (alternative)" 
                    "    REFERENCES course(ID)"
                    "    ON DELETE CASCADE);"
                    )
    '''
    createIntroSQL = ("CREATE TABLE introductory_sequences ("
                      "`id`     INTEGER,"
                      "first    VARCHAR(12),"
                      "second   VARCHAR(12),"
                      "third    VARCHAR(12),"
                      "PRIMARY KEY (`id`));"
                      )

    createGESQL = ("CREATE TABLE gearea ("
                    "`id`   INTEGER AUTO_INCREMENT,"
                    "area   VARCHAR(10),"
                    "title  VARCHAR(50),"
                    "PRIMARY KEY (id));"
                    )

    createTablesSQLList = [createDegreeSQL, createCourseSQL, createDegreeCourseSQL, createIntroSQL, createGESQL]

    # COLUMN NAMES
    degreeColumns = "title, programname, totalunits,requiredcourseunits,techelectiveunits, supportcourseunits, freeelectiveunits,geunits,requirements,gpa"
    courseColumns = "department,code,title,units,lectures,labs,quarters, gearea, prerequisites, grad, division, level"
    degreeCourseColumns = "degree,course,fulfills"
    alternativesColumns = "ogcourse, alternative"    
    introColumns = "id, first, second, third"
    geColumns = "area, title"
    #prerequisitesColumns = "ogcourse, prerequisite, mingrade, consent"
    #otherPrerequisitesColumns = "ogcourse,prerequisite"

    #  PREPARED INSERT STATEMENTS
    insertDegreeSQL = "INSERT INTO degree(" + degreeColumns + ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    insertCourseSQL = "INSERT IGNORE INTO course(" + courseColumns + ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    insertDegreeCourseSQL = "INSERT INTO degree_courses(" + degreeCourseColumns + ") VALUES (%s,%s,%s);"
    insertIntroSQL = "INSERT INTO introductory_sequences(" + introColumns + ") VALUES (%s,%s,%s,%s);"
    insertGESQL = "INSERT INTO gearea(" + geColumns + ") VALUES (%s,%s);"
    #insertAltSQL = "INSERT INTO alternatives(" + alternativesColumns + ") VALUES (%s,%s);"
    #insertPreReqSQL = "INSERT INTO prerequisites(" + prerequisitesColumns + ") VALUES (%s,%s,%s,%s);"
    #insertOtherPreReqSQL = "INSERT INTO other_prerequisites (" + otherPrerequisitesColumns + ") VALUES (%s,%s);"

    # prepared degree_course statements
    findDegreeIdSQL = "SELECT id FROM degree WHERE title=%s AND programname = %s;"
    findCourseIdSQL = "SELECT id FROM course WHERE department = %s AND code = %s;"

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='pglucas466',
                                 password='pglucasdb466',
                                 db='pglucas466',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:

            # drop all tables
            for stmt in dropTablesSQLList:
                cursor.execute(stmt)
                connection.commit()

            # create all tables
            for stmt in createTablesSQLList:
                cursor.execute(stmt)
                connection.commit()

            '''
            # check to see if they were added
            cursor.execute("SHOW TABLES;")
            createdTables = cursor.fetchall()
            print(createdTables)

            cursor.execute("SELECT * FROM degree;")
            createdTables = cursor.fetchall()
            print(createdTables)
            '''
            # ADD COURSE INFO
            coursesInfo = get_courses_info()
            values = parseCourses(coursesInfo)
            cursor.executemany(insertCourseSQL,values)
            connection.commit()

            # ADD MINOR INFO
            minorInfo = get_minor_courses()
            minor, intro, insertCourses, minorCourses = parseMinor(minorInfo)

            # save minor info in degree table
            cursor.execute(insertDegreeSQL,minor)
            connection.commit()

            # populate intro_sequences table
            cursor.executemany(insertIntroSQL, intro)
            connection.commit()

            # insert extra courses if they don't already exist
            cursor.executemany(insertCourseSQL,insertCourses)
            connection.commit()

            # insert degree relations
            # get id for minor
            cursor.execute(findDegreeIdSQL, ("STAT","Minor"))
            d_id = cursor.fetchone()["id"]

            for pair in minorCourses:
                # get id for course
                cursor.execute(findCourseIdSQL, (pair[0],pair[1]))
                c_id = cursor.fetchone()["id"]
                # insert relation into degree_courses
                cursor.execute(insertDegreeCourseSQL, (d_id,c_id,"required"))
                connection.commit()
            
            # ADD MAJOR INFO
            majorInfo = get_major_info()
            major, req_courses, electives, support, ge = parseMajor(majorInfo)

            # save major info in degree table
            cursor.execute(insertDegreeSQL,major)
            connection.commit()

            # get id of degree
            cursor.execute(findDegreeIdSQL, ("STAT","Major"))
            d_id = cursor.fetchone()["id"]
            
            # insert extra courses if they don't already exist
            cursor.executemany(insertCourseSQL, req_courses)
            connection.commit()

            for pair in req_courses:
                # get id for course
                cursor.execute(findCourseIdSQL, (pair[0],pair[1]))
                c_id = cursor.fetchone()["id"]
                # insert relation into degree_courses
                cursor.execute(insertDegreeCourseSQL, (d_id,c_id,"required"))
                connection.commit()

            cursor.executemany(insertCourseSQL, electives)
            connection.commit()

            for pair in electives:
                # get id for course
                cursor.execute(findCourseIdSQL, (pair[0],pair[1]))
                c_id = cursor.fetchone()["id"]
                # insert relation into degree_courses
                cursor.execute(insertDegreeCourseSQL, (d_id,c_id,"techelective"))
                connection.commit()

            cursor.executemany(insertCourseSQL, support)
            connection.commit()

            for pair in support:
                # get id for course
                cursor.execute(findCourseIdSQL, (pair[0],pair[1]))
                c_id = cursor.fetchone()["id"]
                # insert relation into degree_courses
                cursor.execute(insertDegreeCourseSQL, (d_id,c_id,"support"))
                connection.commit()

            # populate ge table
            cursor.executemany(insertGESQL,ge)
            connection.commit() 
           
    except Exception as e:
        print('Got error {!r}, errno is {}'.format(e, e.args[0]))
    finally:
        connection.close

    return

if __name__ == "__main__":
    main()
