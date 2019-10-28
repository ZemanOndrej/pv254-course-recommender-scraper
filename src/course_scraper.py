from util import safe_get_element_by_xpath
import re
xpaths_text = {
    'overview': '//div[@data-expand-article-target="overview"]',
    'name': '//h1[@id="course-title"]',
    'school': '//div[@class="classcentral-style"]//p//a[@class="text--charcoal hover-text--underline"]',
    'provider': '//div[@class="classcentral-style"]//p//a[@class="text--charcoal text--italic hover-text--underline"]',
    'categories': '//div[@class="text-2 margin-top-xsmall margin-bottom-small medium-up-margin-bottom-xxsmall"]',
    'syllabus': '//div[@data-expand-article-target="syllabus"]',
    'teachers': '//div[@class="text-1 margin-top-medium"]//div[@class="col width-100 text-2 medium-up-text-1"]',

}

xpaths_other = {
    'link': '//a[@id="btnProviderCoursePage"]'
}


class CourseScraper:
    def __init__(self, driver):
        self.driver = driver

    def scrape_course_reviews(self):
        current_page = 1
        reviews = self.driver.find_elements_by_xpath(
            '//div[@class="border-all  border--gray-xlight radius padding-large single-review margin-top-medium margin-bottom-large"]')
        parsed_reviews = []
        for rev in reviews:
            review = {}
            rev_id = rev.get_attribute('id')
            review['id'] = rev_id
            review['username'] = rev.find_element_by_xpath(
                '//strong[@class="unit-block unit-fill text-2 text--bold"]').text
            review['rating'] = rev.find_element_by_xpath(
                '//span[@class="review-rating medium-up-hidden text--charcoal"]').get_attribute('textContent').strip()

            els = rev.find_elements_by_xpath(
                f'//div[@id="{rev_id}"]//div[@class="review-title title-with-image margin-top-xsmall text-2"]/span/strong')
            review['adjs'] = [x.text for x in els]

            try:
                rev.find_element_by_xpath(
                    '//button[@class="text-2 icon--right icon-chevron-down-blue text--blue"]').click()
            except:
                print('shiet')

            review['text'] = rev.find_element_by_xpath(
                f"""//div[@data-expand-target="{review['id']}"]""").text

            parsed_reviews.append(review)

        # only one page
        return parsed_reviews

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

        course['rating'] = safe_get_element_by_xpath(
            self.driver, '//span[@class="review-rating hidden text--charcoal"]', 'rating').get_attribute('textContent').strip()

        if course['teachers'] is not None:
            course['teachers'] = [x.strip()
                                  for x in re.split(',|and |& ', course['teachers'])]
        else:
            course['teachers'] = []

        course['categories'] = [x.strip()
                                for x in course['categories'].replace('Found in ', '').split(',')]

        details = [x.text for x in self.driver.find_elements_by_xpath(
            '//div[@class="shadow border-all border--xgray border--thin"]/ul/li')]

        course['details'] = parse_course_details(details)

        return course


def parse_course_details(details):
    detail_data = {}
    for x in details[:-1]:
        det_split = x.split('\n')
        if len(det_split) == 0:
            continue
        detail_name = det_split[0].lower()

        if len(det_split) == 1:
            detail_data[detail_name] = None
        elif len(det_split) == 2:
            detail_data[detail_name] = det_split[1]
        elif len(det_split) > 2:
            detail_data[detail_name] = det_split[1:]

    return detail_data
