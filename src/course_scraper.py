import re
from json import loads
from selenium.common.exceptions import NoSuchElementException

xpaths_text = {
    'overview': '//div[@data-expand-article-target="overview"]',
    'name': '//h1[@id="course-title"]',
    'provider': '//p[@class="text-1 block large-up-inline-block z-high relative"]/a[@class="color-charcoal italic hover-text-underline" and @data-track-click="course_click"]',
    'categories': '//div[@class="text-2 margin-top-xsmall margin-bottom-small medium-up-margin-bottom-xxsmall"]',
    'syllabus': '//div[@data-expand-article-target="syllabus"]',
    'teachers': '//div[@class="text-1 margin-top-medium"]//div[@class="row"]//div[@class="col width-100 text-1"]',
    # 'review_count': '//a[@class="text-4 text-charcoal hover-text-underline medium-up-text-3 padding-horz-xsmall"]',
    'interested_count': '//div[@class="margin-top-small row nowrap vert-align-middle"]//strong[@class="text-3 weight-semi inline-block"]'

}

xpaths_other = {
    'school': '//p[@class="text-1 block large-up-inline-block z-high relative"]/a[@class="color-charcoal hover-text-underline" ]',
    'link': '//a[@id="btnProviderCoursePage"]',
    'rating': '//span[@class="review-rating hidden text-charcoal"]',
    'details': '//div[@class="shadow-light radius-small border-all border-gray-light medium-down-margin-top-small"]/ul[@class="list-no-style"]/li'
}


missing_atrs = {}


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

    def scrapeCourse(self, subject, id):
        course = {}
        self.id = id
        course['subject'] = subject
        course['id'] = id
        for x in xpaths_text:
            course[x] = self.safe_get_element_by_xpath(
                xpaths_text[x], atrName=x)
            if course[x] is not None:
                course[x] = course[x].text

        scriptTag = self.safe_get_element_by_xpath(
            '/html/body/div[1]/div/script').get_attribute('innerHTML')
        js = loads(scriptTag, strict=False)

        course['description'] = js['description']
        course['rating'] = js['aggregateRating']['ratingValue']
        course['review_count'] = js['aggregateRating']['reviewCount']
        course['link'] = self.safe_get_element_by_xpath(
            xpaths_other['link']).get_attribute('href')

        if course['teachers'] is not None:
            course['teachers'] = [x.strip()
                                  for x in re.split(',|and |& ', course['teachers'])]
        else:
            course['teachers'] = []

        course['categories'] = [x.strip()
                                for x in course['categories'].replace('Found in ', '').split(',')]


        course['schools']= [x.text for x in self.safe_get_elements_by_xpath(xpaths_other['school'])]



        details = [x.text for x in self.driver.find_elements_by_xpath(
            xpaths_other['details'])]

        course['details'] = parse_course_details(details)
        return course

    def safe_get_element_by_xpath(self, xpath, atrName=''):
        try:
            return self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            print(f'no atribute({atrName})',flush=True)
            if atrName in missing_atrs:
                missing_atrs[atrName].append(self.id)
            else:
                missing_atrs[atrName] = []
            return None

    def safe_get_elements_by_xpath(self, xpath, atrName=''):
        try:
            return self.driver.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            print(f'no atribute({atrName})',flush=True)
            if atrName in missing_atrs:
                missing_atrs[atrName].append(self.id)
            else:
                missing_atrs[atrName] = []
            return None


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
