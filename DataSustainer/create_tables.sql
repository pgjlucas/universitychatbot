/*
    StaCIA Database Set Up

    Creating tables and relations to be 
    filled in by the data sustainer
*/

-- USE mkong02466;

/*QUESTION DEFINITON AND RELATIONS*/


/*DEGREE DEFINITION AND RELATIONS*/
CREATE TABLE IF NOT EXISTS degree (
    id                 INTEGER AUTO_INCREMENT,
    title              VARCHAR(6) NOT NULL,
    totalunits         INTEGER NOT NULL,
    reqcourseunits     INTEGER NOT NULL,
    techelectiveunits  INTEGER,
    supportcourseunits INTEGER,
    freeelectiveunits  INTEGER,
    geunits            INTEGER,

    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS degree_courses (
    degree   INTEGER,
    course   INTEGER,
    fulfills VARCHAR(20),

    PRIMARY KEY (degree,course),
    FOREIGN KEY (degree) 
        REFERENCES degree(id)
        ON DELETE CASCADE,
    FOREIGN KEY (course) 
        REFERENCES course(id)
        ON DELETE CASCADE
);
/*Fulfills: required, techelective, support, ge*/


/*COURSE DEFINITION AND RELATIONS*/

CREATE TABLE IF NOT EXISTS course (
    id         INTEGER AUTO_INCREMENT,
    department CHAR(4) NOT NULL,
    code       INTEGER NOT NULL,
    title      VARCHAR(100) NOT NULL,
    units      INTEGER NOT NULL,
    lectures   INTEGER NOT NULL,
    labs       INTEGER NOT NULL,
    quarter    CHAR(3) NOT NULL,
    gearea     INTEGER,

    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS prerequisites (
    ogcourse     INTEGER,
    prerequisite INTEGER,
    mingrade     CHAR(2),
    consent      BOOLEAN,

    PRIMARY KEY (ogcourse, prerequisite),
    FOREIGN KEY (ogcourse) 
        REFERENCES course(ID)
        ON DELETE CASCADE,
    FOREIGN KEY (prerequisite) 
        REFERENCES course(ID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alternatives (
    ogcourse    INTEGER,
    alternative INTEGER,

    PRIMARY KEY (ogcourse, alternative),
    FOREIGN KEY (ogcourse) 
        REFERENCES course(ID)
        ON DELETE CASCADE,
    FOREIGN KEY (alternative) 
        REFERENCES course(ID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS other_prerequisites (
    ogcourse     INTEGER,
    prerequisite VARCHAR(50),

    PRIMARY KEY (ogcourse),
    FOREIGN KEY (ogcourse)
        REFERENCES course(id)
        ON DELETE CASCADE
);