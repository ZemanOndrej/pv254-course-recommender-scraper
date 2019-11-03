import logging
import re
import sys
import json

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from course_scraper import CourseScraper, missing_atrs
from util import get_course_id, get_subject_urls, saveJson
from course_url_scraper import CourseUrlsScraper

done_subjects = ['cs']
all_subjects = ['business', 'humanities', 'data-science', 'personal-development', 'programming-and-software-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]

impl_wait = 2

def setup(opts=None):
    logging.basicConfig(filename='scraper.log', level=logging.DEBUG)
    driver = webdriver.Firefox(options=opts)
    driver.implicitly_wait(impl_wait)
    return driver


def scrape_urls(subs):
    driver = setup()
    s = CourseUrlsScraper(driver)
    s.scrape_all_subjects(subs)
    driver.quit()


def save_missing_attrs():
    obj = {}
    with open('missing_atrs.json', 'r') as f:
        obj = json.loads(f.read())

    for key in obj:
        obj[key] = set(obj[key])

    for atr in missing_atrs:
        if atr not in obj:
            obj[atr] = missing_atrs[atr]
        else:
            obj[atr].update(missing_atrs[atr])

    with open('missing_atrs.json', 'w') as f:
        f.write(json.dumps(obj))


def scrape_data(subs=None):
    subs = ['maths'] if subs is None else subs
    options = Options()
    options.add_argument("--headless")
    driver = setup(options)
    output = {}

    for sub in subs:
        print(f'starting subject {sub}')
        arr = get_subject_urls(sub)
        cs = CourseScraper(driver)
        for i, url in enumerate(arr):
            driver.get(url)
            course_id = get_course_id(url)
            try:
                output[course_id] = cs.scrapeCourse(sub, id=course_id)
            except Exception as e:
                print(e)
                logging.error(e)
                save_missing_attrs()
                driver.quit()
            print(f'courseid={course_id} --- {i}/{len(arr)}')
            logging.info(f'courseid={course_id} --- {i}/{len(arr)}')

        saveJson(output, f'./courses/data/{sub}_courses.json')
    save_missing_attrs()
    driver.quit()


def main(subs=None):
    scrape_data(subs)


def parse_params():
    args = sys.argv
    if len(args) <= 1:
        print('running scraper on maths')
        return None
    elif args[1] == 'help':
        print('--subjects (list all subjects); --all (run scraper with all subjects); maths cs ... to run specified courses')
        exit()
    elif args[1] == '--subjects':
        print(all_subjects)
        exit()
    elif args[1] == '--all':
        print('running scraper with all subjects')
        return all_subjects
    elif all(x in all_subjects for x in args[1:]):
        print('running scraper with these subjects' + repr(args[1:]))
        return args[1:]
    else:
        print('wrong command')
        exit()


if __name__ == '__main__':
    arr = parse_params()
    main(arr)
