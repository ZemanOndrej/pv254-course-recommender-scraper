from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
from util import get_course_id, saveJson, get_subject_urls
from course_scraper import CourseScraper

all_subjects = ['cs', 'business', 'humanities', 'data-science', 'personal-development', 'programming-and-software-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]


def main():
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    output = {}


    subs = ['maths']
    for sub in subs:
        arr = get_subject_urls(sub)
        cs = CourseScraper(driver)
        i = 0
        for url in arr:
            driver.get(url)
            course_id = get_course_id(url)
            try:
                output[course_id] = cs.scrapeCourse(sub)
            except Exception as e:
                print(e)
                driver.quit()
            print(course_id+f'{i}/{len(arr)}')
            i+=1


        saveJson(output, f'./courses/data/{sub}_courses.json')
    driver.quit()


if __name__ == '__main__':
    main()
