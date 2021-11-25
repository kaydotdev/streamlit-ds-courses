import os
import sys
import logging
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


TIMEOUT_SEC = 5

dataframe = pd.DataFrame(columns=['url', 'title', 'authors', 'rating', 'votes_count',
                                  'students_count', 'level', 'platform', 'free'])

native_logger = logging.getLogger()
native_logger.setLevel(logging.INFO)
native_logger.addHandler(logging.StreamHandler(sys.stdout))

native_logger.info("[Driver] Initiating driver")
driver = webdriver.Chrome(os.environ['CHROME_DRIVER'])
native_logger.info("[Driver] Driver is ready")


def safe_check_by_selector_text(__driver__, __selector__):
    try:
        return WebDriverWait(__driver__, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, __selector__))).text
    except TimeoutException:
        return None


def safe_check_by_selector_href(__driver__, __selector__):
    try:
        return WebDriverWait(__driver__, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, __selector__))).get_attribute('href')
    except TimeoutException:
        return None


for page_id in range(100):
    driver.get("https://www.coursera.org/search?index=prod_all_launched_products_term_optimization&"
               f"topic=Data%20Science&page={page_id + 1}")

    try:
        courses_page = WebDriverWait(driver, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.ais-InfiniteHits-list')))

        for course in courses_page.find_elements(By.CSS_SELECTOR, 'li.ais-InfiniteHits-item'):
            record_base = {
                'url': safe_check_by_selector_href(course, 'a.result-title-link'),
                'title': safe_check_by_selector_text(course, 'h2.card-title'),
                'authors': [safe_check_by_selector_text(course, 'span.partner-name')],
                'rating': safe_check_by_selector_text(course, 'span.ratings-text'),
                'votes_count': safe_check_by_selector_text(course, 'span.ratings-count span'),
                'students_count': safe_check_by_selector_text(course, 'div.enrollment span.enrollment-number'),
                'level': safe_check_by_selector_text(course, 'span.difficulty'),
                'platform': 'Coursera',
                'free': False
            }

            native_logger.info(f"[Queue] Recording entity: {record_base}")
            dataframe = dataframe.append(record_base, ignore_index=True)
    except Exception as ex:
        native_logger.error(f"[Driver] Aborting next crawling due to error: {ex}")

dataframe.to_json("coursera_header.json", orient="records")
driver.close()
