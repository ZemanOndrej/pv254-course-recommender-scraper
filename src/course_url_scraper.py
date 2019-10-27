from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from util import saveJson
from selenium.webdriver.common.by import By

from main import all_subjects


class CouseUrlsScraper:
    def __init(self, driver, subjects):
        self.driver = driver
        self.subjects = subjects

    def get_subject_course_urls(self, subject):
        subject_course_url = f'https://www.classcentral.com/subject/{subject}'
        json_output = {}
        self.driver.get(subject_course_url)
        show_more_button = self.driver.find_element_by_id('show-more-courses')
        is_displayed = show_more_button.is_displayed()
        slidein = self.driver.find_element_by_id('signup-slidein')
        while show_more_button.is_displayed():
            try:

                if slidein.is_displayed():
                    self.driver.execute_script(
                        "document.getElementById('signup-slidein').style.display = 'none';")

                element = ui.WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.ID, 'show-more-courses')))
                element.click()
            except:
                print('error')

        course_url_btns = self.driver.find_elements_by_xpath(
            '//a[@class="text--charcoal text-2 medium-up-text-1 block course-name" and @itemprop="url"]')

        course_urls = [x.get_attribute('href') for x in course_url_btns]
        saveJson(course_urls, f'./courses/urls/{subject}_courses.json')

    def scrape_all_subjects(self):
        for subject in all_subjects:
            get_subject_course_urls(subject)
