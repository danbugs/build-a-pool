import requests
from bs4 import BeautifulSoup
import re
import json

def sortPrerequisites(prereqtext, minGradetext):
    this_prereqs=""
    if(prereqtext.find("one of")>0):
        values = prereqtext.split("one of ")
        courses = values[1]
        this_prereqs = minGradetext + "OR("+courses.strip(".\n")+")"
    elif(prereqtext.find("all of")>0):
        values = prereqtext.split("all of ")
        courses = values[1]
        this_prereqs = minGradetext + "AND("+courses.strip(".\n")+")"
    elif(prereqtext.find("higher in one of")>0):
        values = prereqtext.split("higher in one of ")
        courses = values[1]
        this_prereqs = minGradetext + "OR("+courses.strip(".\n")+")"
    elif(prereqtext.find("higher in all of")>0):
        values = prereqtext.split("higher in all of ")
        courses = values[1]
        this_prereqs = minGradetext + "AND("+courses.strip(".\n")+")"
    elif(prereqtext.find("higher in")>0):
        values = prereqtext.split("higher in ")
        courses = values[1]
        this_prereqs = minGradetext + "AND("+courses.strip(".\n")+")"
    elif(prereqtext.find("in")>0):
        values = prereqtext.split("in ")
        courses = values[1]
        this_prereqs = minGradetext +"("+courses.strip(".\n")+")"
    return this_prereqs

courseANDdesc = dict()
courseIDList = []
coursePrereqs = []
courseCoreqs = []
coursePrereqsOR = []
URL = "http://www.calendar.ubc.ca/okanagan/courses.cfm?code=cosc"
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find( id="UbcMainContent")

course_names_raw = results.find_all('dt')

for courseID in course_names_raw:
    value = ((courseID.text)[0:8]).replace(" ", "")
    courseIDList.append(value)

course_descriptions_raw = results.find_all('dd')
index = 0
for prereq in course_descriptions_raw:
    values = []
    this_course_prereqs=[]
    if((prereq.text).find("Prerequisite:") > 0):
        values = prereq.text.split("Prerequisite:")
        pre = values[1]
        if(pre.find("Corequisite:") > 0):
            values = pre.split("Corequisite:")
            pre = values[0]
        if(pre.find("Equivalency:") > 0):
            values = pre.split("Equivalency:")
            pre = values[0]
        pre = pre.replace("Third-year standing", " 3rd ")
        pre = pre.replace("Fourth-year standing.\n", " 4th ")
        pre = pre.replace("third-year standing", " 3rd ")
        if(pre.find("A score") > 0):
            values = pre.split("%")
            #minGrade = (values[0])[-2:]
            minGrade = ""
            if(len(values)>2):
                #minGrade2 = (values[1])[-2:]
                minGrade2 = ""
                parts = pre.split("and a score")
                if(parts[1].find(".")>0):
                    another_part = parts[1].split(". ")
                if(parts[0].find("and")>0):
                    parts[0] = parts[0].replace(" and ", ",")
                if(another_part[0].find("and")>0):
                    another_part[0] = another_part[0].replace(" and ", ",")
                this_course_prereqs.append(sortPrerequisites(parts[0], minGrade))
                this_course_prereqs.append(sortPrerequisites(another_part[0], minGrade2))

            else:
                if(pre.find("and")>0):
                    pre = pre.replace(" and ", ",")
                this_course_prereqs.append(sortPrerequisites(pre, minGrade))
        elif(pre.find("One of")>0):
            values = pre.split("One of ")
            courses = values[1]
            if(courses.find("one of") > 0):
                first_or = courses.split(" and ")
                first_or_courses = first_or[0]
                more_courses = first_or[1].strip("one of ")
                all_reqs = "OR("+first_or_courses+")"+"AND(OR("+more_courses.strip(". \n")+")"
            else:
                if(courses.find("and")>0):
                    courses = courses.replace(" and ", ",")
                all_reqs = "OR("+courses.strip(". \n")+"))"
            this_course_prereqs.append(all_reqs)
        elif(pre.find("All of")>0):
            values = pre.split("All of ")
            courses = values[1]
            if(courses.find("one of") > 0):
                first_or = courses.split(" and ")
                first_or_courses = first_or[0]
                more_courses = first_or[1].strip("one of ")
                text = "AND("+ first_or[0] + "AND(OR("+ more_courses.strip(". \n")+"))"
            elif(courses.find("and") > 0 and courses.find("60% or higher in") > 0):
                courses = courses.replace(" and a score of 60% or higher in",",")
                text = "AND("+courses.strip(".\n")+")"
            elif(courses.find("60% or higher in") > 0):
                second_course = pre.split("and a score of 60% or higher in")
                text = "AND(" + courses[0:17] + "(OR("+second_course[1].strip(".\n")+"))"
            elif(courses.find("and") > 0):
                more_courses = courses.split(" and ")
                text = "AND(" + more_courses[0]+", "+more_courses[1]+")"
            else:
                text = "AND("+courses.strip(". \n")+"))"
            this_course_prereqs.append(text)
        elif(pre.find("Third-year")>0):
            this_prereqs = []
            values = pre.split("Third-year ")
            courses = values[1]
            this_prereqs.append("AND("+courses.strip(".\n")+"))")
            this_course_prereqs.append(this_prereqs)
        elif(pre.find("Either")>0):
            optionA = pre.split("a) ")
            valueA = optionA[1]
            prereq_1 = valueA[0:9]
            optionB = pre.split("b) ")
            valueB = optionB[1]
            prereq_2 = valueB
            if(valueB.find("of")>0):
                courses_either = valueB.strip("one of ")
                courses_either_list = courses_either.replace(" or", ",")
                prereq_2 = courses_either_list.strip(".\n")
            extra=""
            if(valueB.find(" is required")>0):
                extra = ", 3rd"
            if(prereq_2.find(" or ") > 0):
                prereq_2 = prereq_2.split(" or ")
            this_course_prereqs.append("OR("+prereq_1.strip(", or")+", "+prereq_2+extra+"))")
        else:
            if(pre.find("3rd")>0):
                text = "3rd"
            elif(pre.find("Fourth")>0):
                text="4th"
            else:
                text = pre[0:9]
            if(pre.find("and a score") > 0):
                second_course = pre.split("and a score of 60% or higher in")
                text = "OR(" + pre[0:9] + ", "+second_course[1].strip(".\n")+")"
            if(pre.find("one of") > 0):
                list_courses = pre.split("and one of")
                if(len(list_courses)>2):
                    text = "AND("+list_courses[0]+"(OR("+list_courses[1]+")OR("+list_courses[2].strip(". \n")+")"
                else:
                    text = "AND("+list_courses[0]+")"+"OR("+list_courses[1].strip(". \n")+")"
            this_course_prereqs.append(text)
        coursePrereqs.append(this_course_prereqs)

    else:
        coursePrereqs.append("")

    if((prereq.text).find("Corequisite:") > 0):
        values = prereq.text.split("Corequisite:")
        final_val = values[1].strip(".\n")
        final_val = final_val.strip("One of ")
        courseCoreqs.append(final_val)
    else:
        courseCoreqs.append("")

#Dictionaryyyyyy
filename = "MERMAID.txt"
with open(filename, 'w') as outfile:
    THE_dict = {}
    orCounter = 0
    andCounter = 1000
    for index in range(0, len(coursePrereqs)-1):
        current_el = coursePrereqs[index]
        if(len(current_el) > 0):
            current_el_text = current_el[0]
            if(current_el_text[0:2] == "OR"):
                if(current_el_text.find("AND") > 0):
                    orStuff = current_el_text.replace("OR(", "")
                    orStuff = orStuff.replace(" ", "")
                    subAND = orStuff.split(")AND(")
                    subAND[0] = subAND[0].split(",")
                    subAND[1] = subAND[1].split(",")
                    for codes in subAND[0]:
                        outfile.write(((codes.replace(" ", "")).replace(".", ""))+"("+(codes.replace(" ", "")).replace(".", "")+")-->"+str(orCounter)+"{OR}\n")
                    outfile.write(str(orCounter)+"{OR}-->"+str(andCounter)+"{AND}\n")
                    orCounter = orCounter + 1
                    outfile.write(str(orCounter)+"{OR}-->"+str(andCounter)+"{AND}\n")
                    for codes in subAND[1]:
                            outfile.write((codes.replace(" ", "")).replace(".", "").replace(")","")+"("+(codes.replace(" ", "")).replace(".", "").replace(")","")+")-->"+str(orCounter)+"{OR}\n")
                    orCounter = orCounter + 1
                    outfile.write(str(andCounter)+"{AND}-->"+courseIDList[index].replace(" ", "")+"("+courseIDList[index].replace(" ", "")+")\n")
                    andCounter = andCounter + 1
                    THE_dict[courseIDList[index]]={"id":courseIDList[index],"preq":{"and":{"or1":subAND[0], "or2":subAND[1]}}}
                else:
                    courses_format = current_el_text.replace("OR(", "")
                    courses_format = courses_format.replace(")", "")
                    courses_format = courses_format.replace(" ", "")
                    course_codesOR = courses_format.split(",")
                    for codes in course_codesOR:
                        if(codes.find("\n") < 0):
                            outfile.write(codes.replace(" ", "")+"("+codes.replace(" ", "")+")-->"+str(orCounter)+"{OR}\n")
                    outfile.write(str(orCounter)+"{OR}-->"+courseIDList[index].replace(" ", "")+"("+courseIDList[index].replace(" ", "")+")\n")
                    orCounter = orCounter + 1
                    THE_dict[courseIDList[index]]={"id":courseIDList[index],"preq":{"or":course_codesOR}}
            elif(current_el_text[0:3] == "AND"):
                if(current_el_text.find("OR")>0):
                    andStuff = current_el_text.replace("AND(", "")
                    andStuff = andStuff.replace(" ", "")
                    subOR = andStuff.split("OR(")
                    subOR[0] = subOR[0].split(",")
                    subOR[1] = subOR[1].split(",")
                    for codes in subOR[0]:
                        outfile.write(((codes.replace(" ", "")).replace(".", "")).replace("(","").replace(")","")+"("+(codes.replace(" ", "")).replace(".", "").replace("(","").replace(")","")+")-->"+str(andCounter)+"{AND}\n")
                    for codes in subOR[1]:
                        outfile.write((codes.replace(" ", "")).replace(".", "").replace(")","")+"("+(codes.replace(" ", "")).replace(".", "").replace(")","")+")-->"+str(orCounter)+"{OR}\n")
                    if(len(subOR)==2):
                        outfile.write(str(orCounter)+"{OR}-->"+str(andCounter)+"{AND}\n")
                    else:
                        subOR[2] = subOR[2].split(",")
                        outfile.write(str(orCounter)+"{OR}-->"+str(andCounter)+"{AND}\n")
                        orCounter = orCounter+1
                        for codes in subOR[2]:
                            outfile.write((codes.replace(" ", "")).replace(".", "").replace(")","")+"("+(codes.replace(" ", "")).replace(".", "").replace(")","")+")-->"+str(orCounter)+"{OR}\n")
                        outfile.write(str(orCounter)+"{OR}-->"+str(andCounter)+"{AND}\n")
                    outfile.write(str(andCounter)+"{AND}-->"+courseIDList[index].replace(" ", "")+"("+courseIDList[index].replace(" ", "")+")\n")
                    orCounter = orCounter + 1
                    andCounter = andCounter + 1
                    THE_dict[courseIDList[index]]={"id":courseIDList[index],"preq":{"and":{"and":subOR[0], "or":subOR[1]}}}
                else:
                    courses_format = current_el_text.replace("AND(", "")
                    courses_format = courses_format.replace(")", "")
                    courses_format = courses_format.replace(" ", "")
                    course_codes_AND = courses_format.split(",")
                    for codes in course_codes_AND:
                        if(len(course_codes_AND) > 1):
                            outfile.write((codes.replace(" ", "")).replace(".", "")+"("+(codes.replace(" ", "")).replace(".", "")+")-->"+str(andCounter)+"{AND}\n")
                    if(len(course_codes_AND) > 1):
                        outfile.write(str(andCounter)+"{AND}-->"+courseIDList[index].replace(" ", "")+"("+courseIDList[index].replace(" ", "")+")\n")
                    else:
                        outfile.write(course_codes_AND[0].replace(" ", "")+"-->"+courseIDList[index]+"\n")
                    andCounter = andCounter + 1
                    THE_dict[courseIDList[index]]={"id":courseIDList[index],"preq":{"and":course_codes_AND}}
            else:
                outfile.write(current_el_text.replace(" ", "").replace("(","").replace(")", "")+"("+current_el_text.replace(" ", "").replace("(","").replace(")", "")+")-->"+courseIDList[index]+"\n")
                THE_dict[courseIDList[index]]={"id":courseIDList[index],"preq":current_el_text}
        else:
            THE_dict[courseIDList[index]]={"id":courseIDList[index],"preq":""}

        current_el_coreq = courseCoreqs[index]
        if(len(current_el_coreq) > 0):
            current_el_coreq = current_el_coreq.replace(" ", "")
            list = current_el_coreq.split(",")
            for codes in list:
                if(len(list)>1):
                    outfile.write((codes.replace(" ", "")).replace(".", "").replace(")","")+"("+(codes.replace(" ", "")).replace(".", "").replace(")","")+")---"+str(orCounter)+"{OR}\n")
            if(len(list) > 1):
                    outfile.write(str(orCounter)+"{OR}---"+courseIDList[index].replace(" ", "")+"("+courseIDList[index].replace(" ", "")+")\n")
                    orCounter = orCounter + 1
            else:
                outfile.write(codes.replace(" ", "")+"(" + codes.replace(" ", "")+")---"+courseIDList[index].replace(" ", "")+"("+courseIDList[index].replace(" ", "")+")\n")
            THE_dict[courseIDList[index]].update({"creq":{"or":list}})
        else:
            THE_dict[courseIDList[index]].update({"creq":""})

# filename = "filenotimportant.json"
# with open(filename, 'w') as outfile:
#     json.dump(THE_dict,outfile, sort_keys=False, indent = 4)

# index = 0
# for value in coursePrereqs:
#     print(courseIDList[index])
#     print(value)
#     index= index+1
