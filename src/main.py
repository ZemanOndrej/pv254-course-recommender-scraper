from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
from util import get_course_id, saveJson, get_subject_urls
from course_scraper import CourseScraper
import logging
from selenium.webdriver.firefox.options import Options
import sys

all_subjects = ['cs', 'business', 'humanities', 'data-science', 'personal-development', 'programming-and-software-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]


def main(subs=None):
    subs = ['maths'] if subs is None else subs
    logging.basicConfig(filename='scraper.log', level=logging.DEBUG)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(5)
    output = {}

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


def parse_params():
    args = sys.argv
    if len(args) <= 1:
        print('running scraper on maths')
        return None
    elif args[1]== 'help':
        print('--subjects (list all subjects); --all (run scraper with all subjects); maths cs ... to run specified courses')
        exit()
    elif args[1] == '--subjects':
        print(all_subjects)
        exit()
    elif args[1] == '--all':
        print('running scraper with all subjects')
        return all_subjects
    elif all(x in all_subjects for x in args[1:]):
        print('running scraper with these subjects'+ repr(args[1:]))
        return args[1:]
    else:
        print('wrong command')
        exit()


if __name__ == '__main__':
    arr = parse_params()
    main(arr)
