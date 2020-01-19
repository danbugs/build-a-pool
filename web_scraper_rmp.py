from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import re

import json
import time

SCHOOL = "University of British Columbia - Okanagan"

RATING_RANK = {
    "awesome": 10,
    "awful": -10,
    "average": 0
    }

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

#scrape department to get prof urls
def scrape_department(url):
    browser = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options, service_args=['--verbose', '--log-path=log.log'])
    browser.get(url)

    #enter computer science in dropdown list
    browser.find_element_by_xpath("/html/body/div[1]/a[1]").click()
    line = browser.find_element_by_xpath("/html/body/div[3]/div[4]/div/div[1]/div/div[3]/div/div/input")
    line.send_keys("Computer Science", Keys.ENTER)
    time.sleep(3)
    html = browser.page_source
    browser.close()

    sp = BeautifulSoup(html, 'html.parser')

    url_list = []
    prof_list = sp.find(id="mainContent").find(class_="side-panel").find(class_="result-list")
    for prof in prof_list.find_all("li"):
       # print(prof.prettify())
        link = prof.find("a")["href"]
        link = "https://www.ratemyprofessors.com" + link
        url_list.append(link)

    return url_list


#load all ratings on rmp page
def load_rmp_ratings(url):
    browser = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options, service_args=['--verbose', '--log-path=log.log'])
    browser.get(url)

    #click load more ratings until button is gone
    while True:
        try:
            actions = ActionChains(browser)
            #el = browser.find_elements_by_class_name("Buttons__Button-sc-19xdot-0")
            el = browser.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[4]/div/div[1]/button")
            el.send_keys("\n")
            time.sleep(3)

            print("Clicked: Load more ratings")
        except Exception as e:
            print(e)
            print("All professor ratings loaded")
            source = browser.page_source
            browser.close()
            return source

#scrape prof page to get course ratings 
def scrape_prof(url):
    html_page = load_rmp_ratings(url)
    sp = BeautifulSoup(html_page, "html.parser")

    #page header titles
    prof = sp.find(class_="NameTitle__Name-dowf0z-0").text
    dep = sp.find(class_="NameTitle__Title-dowf0z-1").find('b').text
    helpful_comment = sp.find(class_="HelpfulRating__StyledComments-sc-4ngnti-1 GxNke").text
    print(f"PROFESSOR: {prof} DEPARTMENT: {dep}")

    #dictionary of json data to output
    prof_data = {}
    prof_data["name"] = prof
    prof_data["url"] = url
    prof_data["department"] = dep
    prof_data["comment"] = helpful_comment    

    #sanity school check
    page_school = sp.find(class_="NameTitle__Title-dowf0z-1").find('a', href=True).text
    if not (page_school == SCHOOL):
        print("Not UBC-O")
        return

    ratings = sp.find(id="ratingsList").find_all(class_="RatingsList__RatingsListItem-hn9one-3 dMVBuC")
    print(f"Ratings: {len(ratings)}")

    #iterate through ratings totaling class score
    course_scores = dict()
    for rating in ratings:
        #skip ad wrapper
        if rating.find(class_="RatingsList__AdWrapper-hn9one-1 ghTgvN"):
            continue

        course = rating.find(class_="RatingHeader__StyledClass-sc-1dlkqw1-2").text
        #skip course names that dont have cosc and a number
        if "COSC" not in course:
            continue
        elif len(re.sub("\d+", "", course)) > 4:
            continue
        elif int(''.join(filter(str.isdigit, course))) > 999 :
            continue

        #add course to score dict
        if course not in course_scores.keys():
            course_scores[course] = 0

        r = rating.find_all(class_="RatingValues__RatingValue-sc-6dc747-3")
        quality = r[0].text
        diff = r[1].text

        score = rating.find(class_="EmotionLabel__StyledEmotionLabel-sc-1u525uj-0")
        score = score.contents[1]
        
        course_scores[course] = int(course_scores[course]) + RATING_RANK[score]
        print(f"parse: {course} {quality} {diff} {score}")
   
    for key, value in course_scores.items():
        print(f"{key} {value}")

    #add score info to prof data    
    prof_data["courses"] = [course_scores]

    filename = "COSC.json"
    with open(filename, 'a') as outfile:
        json.dump(prof_data, outfile, ensure_ascii=False, indent=4) #{prof: prof_data}

if __name__ == "__main__":
    #for headless operation
    #Xvfb is required with PyVirtualDisplay

    #clear json file before write up
    with open('COSC.json','w'): pass

    #initial cosc department url
    url = "https://www.ratemyprofessors.com/search.jsp?queryBy=schoolId&schoolName=University+of+British+Columbia+-+Okanagan&schoolID=5436&queryoption=TEACHER"

    prof_urls = scrape_department(url)
    for prof_url in prof_urls:
        scrape_prof(prof_url)

    #turn entire json  object as array
    data = ""
    with open('COSC.json','r') as file:
        data = file.read()
    with open('COSC.json','w') as file:
        file.write(f"[{data}]")

    #url = "https://www.ratemyprofessors.com/ShowRatings.jsp?tid=1918500&showMyProfs=true"
    #scrape_prof(url)

