from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
from util import get_course_id, saveJson, get_subject_urls
from course_scraper import CourseScraper
import logging

all_subjects = ['cs', 'business', 'humanities', 'data-science', 'personal-development', 'programming-and-software-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]


def main():
    logging.basicConfig(filename='scraper.log', level=logging.DEBUG)
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    output = {}

    subs = ['maths']
    for sub in subs:
        arr = get_subject_urls(sub)
        cs = CourseScraper(driver)
        for i, url in enumerate(arr):
            driver.get(url)
            course_id = get_course_id(url)
            try:
                output[course_id] = cs.scrapeCourse(sub)
            except Exception as e:
                print(e)
                logging.error(e)
                driver.quit()
            print(f'courseid={course_id} --- {i}/{len(arr)}')
            logging.info(f'courseid={course_id} --- {i}/{len(arr)}')

        saveJson(output, f'./courses/data/{sub}_courses.json')
    driver.quit()


if __name__ == '__main__':
    main()
