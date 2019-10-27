from util import safe_get_element_by_xpath
import re
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

class CourseScraper:
    def __init__(self,driver):
        self.driver = driver

    def scrapeCourse(self, subject):
        course = {}
        course['subject'] = subject
        for x in xpaths_text:
            course[x] = safe_get_element_by_xpath(
                self.driver, xpaths_text[x], atrName=x)
            if course[x] is not None:
                course[x] = course[x].text

        course['link'] = safe_get_element_by_xpath(
            self.driver, xpaths_other['link']).get_attribute('href')

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
