from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from util import saveJson
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

all_subjects = ['cs', 'business', 'humanities', 'data-science', 'personal-development', 'programming-and-software-development',
                'art-and-design', 'maths', 'health', 'engineering', 'social-sciences', 'science', 'education', ]


xpaths = {
    'show_button': '//button[@class="btn-blue-outline btn-large margin-top-medium text-center" and @data-name="LOAD_MORE"]'
}


class CourseUrlsScraper:
    def __init__(self, driver):
        self.driver = driver

    def get_subject_course_urls(self, subject):
        subject_course_url = f'https://www.classcentral.com/subject/{subject}?'
        json_output = {}
        self.driver.get(subject_course_url)

        try:
            while ui.WebDriverWait(self.driver, 5, ignored_exceptions=[NoSuchElementException, StaleElementReferenceException]).until(
                    lambda x: x.find_element_by_xpath(xpaths['show_button']).is_displayed()):
                try:
                    if self.driver.find_element_by_id('signup-slidein').is_displayed():
                        self.driver.execute_script(
                            "document.getElementById('signup-slidein').style.display = 'none';")

                        self.driver.find_element_by_xpath(
                            xpaths['show_button']).click()
                    ui.WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpaths['show_button']))).click()

                except Exception as e:
                    print(e)
        except TimeoutException as e:
            print('timeout', e)
        course_url_btns = self.driver.find_elements_by_xpath(
            '//a[@class="color-charcoal block course-name" and @itemprop="url"]')

        course_urls = [x.get_attribute('href') for x in course_url_btns]
        saveJson(course_urls, f'./courses/urls/{subject}_courses.json')

    def scrape_all_subjects(self, subs):
        for subject in subs:
            print('start', subject)
            self.get_subject_course_urls(subject)
            print('finish ', subject)
