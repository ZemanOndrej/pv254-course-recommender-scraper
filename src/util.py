import os
import json
from pathlib import Path
from selenium.common.exceptions import NoSuchElementException


def saveJson(json_output, filename='courses.json'):
    file_dir = Path(filename).parent.absolute()
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(json_output, f)


def get_subject_urls(subject):
    with open(f'courses/urls/{subject}_courses.json') as f:
        return json.load(f)


def get_course_id(url):
    course_url = url.split('/')
    return course_url[len(course_url)-1]


def safe_get_element_by_xpath(driver, xpath, atrName=''):
    try:
        return driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        print(f'no atribute({atrName})')
        return None
