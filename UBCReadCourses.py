import requests
from bs4 import BeautifulSoup
import re


courseANDdesc = dict()
courseIDList = []
coursePrereqs = []
courseCoreqs = []
URL = "http://www.calendar.ubc.ca/okanagan/courses.cfm?code=cosc"
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find( id="UbcMainContent")

course_names_raw = results.find_all('dt')

for courseID in course_names_raw:
    courseIDList.append((courseID.text)[0:8])


course_descriptions_raw = results.find_all('dd')
for prereq in course_descriptions_raw:
    values = []
    if((prereq.text).find("Prerequisite:") > 0):
        values = prereq.text.split("Prerequisite:")
        coursePrereqs.append(values[1])
    else:
        coursePrereqs.append("")

    if((prereq.text).find("Corequisite:") > 0):
        values = prereq.text.split("Corequisite:")
        courseCoreqs.append(values[1])
    else:
        coursePrereqs.append("")


print(courseIDList)
print(coursePrereqs)
print(courseCoreqs)
