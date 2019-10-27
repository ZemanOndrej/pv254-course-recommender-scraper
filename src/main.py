from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import re
import pandas as pd
import os
import json
from pathlib import Path

all_subjects = ['cs', 'business', 'humanities', 'data-science', 'personal-development', 'programming-and-software-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]


xpaths_text = {
    'overview': '//div[@data-expand-article-target="overview"]',
    'name': '//h1[@id="course-title"]',
    'school': '//div[@class="classcentral-style"]//p//a[@class="text--charcoal hover-text--underline"]',
    'provider': '//div[@class="classcentral-style"]//p//a[@class="text--charcoal text--italic hover-text--underline"]',
    'categories': '//div[@class="text-2 margin-top-xsmall margin-bottom-small medium-up-margin-bottom-xxsmall"]',
    'rating': '//span[@class="review-rating hidden text--charcoal"]',
    'syllabus': '//div[@data-expand-article-target="syllabus"]',
    'teachers': '//div[@class="text-1 margin-top-medium"]//div[@class="col width-100 text-2 medium-up-text-1"]',
    'details': '//html/body/div[1]/div[1]/div[3]/div/div[2]/div[1]/div/ul',

}

xpaths_other = {
    'link': '//a[@id="btnProviderCoursePage"]'
}


def saveJson(json_output, filename='courses.json'):
    file_dir = Path(filename).parent.absolute()
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(json_output, f)


def safe_get_element_by_xpath(driver, xpath, atrName=''):
    try:
        return driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        print(f'no atribute({atrName})')
        return None


def parse_course_details(details):
    detail_data = {}
    details_split = details.split('\n')
    start = False
    start_data = []
    for i in range(len(details_split)):
        if start:
            if details_split[i] == 'DURATION':
                start = False
                detail_data[details_split[i]] = details_split[i+1]
                break
            else:
                start_data.append(details_split[i])
                continue

        if i % 2 == 0:
            if details_split[i] == 'START DATE':
                start = True
                detail_data[details_split[i]] = start_data
            else:
                detail_data[details_split[i]] = details_split[i+1]
    return detail_data


def scrapeCourse(output, driver, subject):
    course = {}
    course['subject'] = subject
    for x in xpaths_text:
        course[x] = safe_get_element_by_xpath(
            driver, xpaths_text[x], atrName=x)
        if course[x] is not None:
            course[x] = course[x].text

    course['link'] = safe_get_element_by_xpath(
        driver, xpaths_other['link']).get_attribute('href')

    if course['teachers'] is not None:
        course['teachers'] = [x.strip()
                              for x in re.split(',|and |& ', course['teachers'])]
    else:
        course['teachers'] = []

    course['categories'] = [x.strip()
                                for x in course['categories'].replace('Found in ', '').split(',')]

    course['details'] = parse_course_details(course['details'])

    print(course['name'])
    return course


def get_subject_course_urls(subject, driver):
    subject_course_url = f'https://www.classcentral.com/subject/{subject}'
    json_output = {}
    driver.get(subject_course_url)
    show_more_button = driver.find_element_by_id('show-more-courses')
    is_displayed = show_more_button.is_displayed()
    slidein = driver.find_element_by_id('signup-slidein')
    while show_more_button.is_displayed():
        try:

            if slidein.is_displayed():
                driver.execute_script(
                    "document.getElementById('signup-slidein').style.display = 'none';")

            element = ui.WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'show-more-courses')))
            element.click()
        except:
            print('error')

    course_url_btns = driver.find_elements_by_xpath(
        '//a[@class="text--charcoal text-2 medium-up-text-1 block course-name" and @itemprop="url"]')

    course_urls = [x.get_attribute('href') for x in course_url_btns]
    saveJson(course_urls, f'./courses/urls/{subject}_courses.json')


def scrape_all_subjects(driver):
    for subject in all_subjects:
        get_subject_course_urls(subject, driver)


def get_subject_urls(subject):
    with open(f'courses/urls/{subject}_courses.json') as f:
        return json.load(f)


def get_course_id(url):
    course_url = url.split('/')
    return course_url[len(course_url)-1]


def main():
    driver = webdriver.Firefox()
    driver.implicitly_wait(3)

    sub = 'cs'
    arr = get_subject_urls(sub)
    output = {}
    for url in arr[:3]:
        driver.get(url)
        course_id = get_course_id(url)
        output[course_id] = scrapeCourse(output, driver, sub)
    saveJson(output, f'./courses/data/{sub}_courses.json')
    # print(output)

    # for url in course_urls:
    #     driver.get(url)
    #     course_url = url.split('/')
    #     course_id = course_url[len(course_url)-1]
    #     print(course_id)
    #     # python_button = driver.find_element_by_xpath('//a[@href="'+course_url+'"]')
    #     # button.click()
    #     scrapeCourse(json_output, driver, course_id)
    #     # driver.back()
    # print(course_urls)

    driver.quit()


if __name__ == '__main__':
    main()
