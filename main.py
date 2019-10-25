from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import pandas as pd
import os
import json
from pathlib import Path

href2 = 'https://www.kadenze.com/courses/introduction-to-programming-for-musicians-and-digital-artists/info?utm_campaign=course_catalog&utm_content=course%3D87&utm_medium=referral&utm_source=classcentral'
href = 'http://click.linksynergy.com/fs-bin/click?id=SAyYsTvLiGQ&subid=&offerid=451430.1&type=10&tmpid=18061&RD_PARM1=https%3A%2F%2Fwww.coursera.org%2Flearn%2Fpractical-machine-learning&u1=gtc_search'

all_subjects = ['cs', 'business', 'humanities', 'data-science', 'personal-development', 'programming-and-software-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]


def saveJson(json_output, filename='courses.json'):
    file_dir = Path(filename).parent.absolute()
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(json_output, f)


def scrapeCourse(output, driver, course_id, subject):
    course = {}

    course['overview'] = driver.find_element_by_xpath(
        '//div[@data-expand-article-target="overview"]').text
    course['name'] = driver.find_element_by_id('course-title').text
    course['school'] = driver.find_element_by_xpath(
        '//div[@class="classcentral-style"]//p//a[@class="text--charcoal hover-text--underline"]').text

    course['provider'] = driver.find_element_by_xpath(
        '//div[@class="classcentral-style"]//p//a[@class="text--charcoal text--italic hover-text--underline"]').text

    course['link'] = driver.find_element_by_id(
        'btnProviderCoursePage').get_attribute('href')
    course['categories'] = driver.find_element_by_xpath(
        '//div[@class="text-2 margin-top-xsmall margin-bottom-small medium-up-margin-bottom-xxsmall"]').text
    course['subject'] = subject
    course['sub-categories'] = course['categories'].replace('Found in ', '')

    course['rating'] = driver.find_element_by_xpath(
        '//span[@class="review-rating hidden text--charcoal"]').text

    course['syllabus'] = driver.find_element_by_xpath(
        '//div[@data-expand-article-target="syllabus"]').text

    course['teacher'] = driver.find_element_by_xpath(
        '//div[@class="text-1 margin-top-medium"]//div[@class="col width-100 text-2 medium-up-text-1"]').text
    details = driver.find_element_by_xpath(
        '//html/body/div[1]/div[1]/div[3]/div/div[2]/div[1]/div/ul').text
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
    course['details'] = detail_data
    output[course_id] = course
    print(course['name'])


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
    driver.implicitly_wait(200)

    sub = 'cs'
    arr = get_subject_urls(sub)
    output = {}
    for url in arr[4:15]:
        driver.get(url)
        course_id = get_course_id(url)
        scrapeCourse(output, driver, course_id, sub)
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
