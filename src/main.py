from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
from util import saveJson, get_subject_urls, get_course_id, safe_get_element_by_xpath

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
    driver.quit()


if __name__ == '__main__':
    main()
