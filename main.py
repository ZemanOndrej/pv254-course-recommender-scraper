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

all_subjects = ['cs', 'business', 'humanities', 'data-science', 'personal-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]


def saveJson(json_output, filename='courses.json'):
    file_dir = Path(filename).parent.absolute()
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(filename, 'w') as f:
        json.dump(json_output, f)


def scrapeCourse(output, driver, course_id):
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

    course['rating'] = driver.find_element_by_xpath(
        '//span[@class="review-rating hidden text--charcoal"]//span').text

    course['syllabus'] = driver.find_element_by_xpath(
        '//div[@data-expand-article-target="syllabus"]').text

    course['teacher'] = driver.find_element_by_xpath(
        '//html/body/div[1]/div[1]/div[3]/div/div[3]/section[1]/div[2]/div[2]/div/div').text
    course['details'] = driver.find_element_by_xpath(
        '//html/body/div[1]/div[1]/div[3]/div/div[2]/div[1]/div/ul').text
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


def main():
    driver = webdriver.Firefox()
    driver.implicitly_wait(200)
    subjects = ['programming-and-software-development']

    for subject in subjects:
        get_subject_course_urls(subject, driver)
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
