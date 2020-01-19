from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import json
import time


'''
    get prof url
    scrape data from page, course, ratings for course
    intended format, db, json etc
'''
SCHOOL = "University of British Columbia - Okanagan"

RATING_RANK = {
    "awesome": 10,
    "awful": -10,
    "average": 0
    }

#scrape department to get prof urls
def scrap_department(url):
    print("blah-blah")

#load all ratings on rmp page
def load_rmp_ratings(url):
    browser = webdriver.Chrome()
    browser.get(url)
    wait = WebDriverWait(browser, 5)

    return browser.page_source
    while True:
        try:
            actions = ActionChains(browser)
            el = browser.find_elements_by_class_name("Buttons__Button-sc-19xdot-0")
            for e in el:
                if e.text == "Load More Ratings":
                    if e.is_enabled():
                        actions.move_to_element(e).click().perform()
                        browser.execute_script("arguments[0].scrollIntoView();", e)
                        time.sleep(2)

            print("clicked button")
        except Exception as e:
            print(e)
            print("all prof ratings loaded")
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
    print(f"PROF: {prof} DEP: {dep}")

    prof_data = {}
    prof_data["url"] = url
    prof_data["department"] = dep    

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
        #skip course names that are long
        if int(''.join(filter(str.isdigit, course))) > 999 or "COSC" not in course:
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
    with open(filename, 'w') as outfile:
        json.dump({prof: prof_data}, outfile, ensure_ascii=False, indent=4)
        #json.dump({'courses': course_scores}, outfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    #TODO find url of all professors for section, store url
    url = "https://www.ratemyprofessors.com/ShowRatings.jsp?tid=1918500&showMyProfs=true"
    scrape_prof(url)

