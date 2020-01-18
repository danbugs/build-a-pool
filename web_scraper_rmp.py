from bs4 import BeautifulSoup
import requests
from selenium import webdriver


'''
    get prof url
    scrape data from page, course, ratings for course
    intended format, db, json etc
'''
SCHOOL = "University of British Columbia - Okanagan"

#scrape department to get prof urls
def scrap_department(url):
    print("blah-blah")

#load all ratings on rmp page
def load_rmp_ratings(url):
    browser = webdriver.Chrome()
    browser.get(url)

    try:
        browser.find_element_by_css_selector("#react-tabs-3889349 > button").click()
        print("clicked button")
    except:
        print("all prof ratings loaded")
        return browser.page_source


#scrape prof page to get course ratings 
def scrape_prof(url):
    html_page = load_rmp_ratings(url)
    sp = BeautifulSoup(html_page, "html.parser")

    #page header titles
    prof = sp.find(class_="NameTitle__Name-dowf0z-0").text
    dep = sp.find(class_="NameTitle__Title-dowf0z-1").find('b').text
    print(f"PROF: {prof} DEP: {dep}")    


    #sanity school check
    page_school = sp.find(class_="NameTitle__Title-dowf0z-1").find('a', href=True).text
    if not (page_school == SCHOOL):
        print("Not UBC-O")
        return

    ratings = sp.find(id="ratingsList")
    r = ratings.find_all(class_="RatingsList__RatingsListItem-hn9one-3")
    print(f"Ratings: {len(r)}")



if __name__ == "__main__":
    


    #TODO find url of all professors for section
    url = "https://www.ratemyprofessors.com/ShowRatings.jsp?tid=1918500&showMyProfs=true"
    scrape_prof(url)

