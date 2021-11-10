import os
import sys
import time
import logging
import queue
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

TIMEOUT_SEC = 5

dataframe = pd.DataFrame(columns=['title', 'description', 'authors', 'rating', 'votes_count',
                                  'students_count', 'level', 'duration', 'platform', 'free'])
delayed_requests_queue = queue.Queue()

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


def safe_check_by_selector_attr(__driver__, __selector__, __attribute__):
    try:
        return WebDriverWait(__driver__, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, __selector__))).get_attribute(__attribute__)
    except TimeoutException:
        return None


driver.get("https://www.pluralsight.com/search?q=Data%20Science&categories=course&roles=data-professional")
next_page_available = True

while next_page_available:
    try:
        scroll_anchor = WebDriverWait(driver, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

        for card in scroll_anchor.find_elements(By.CSS_SELECTOR, 'div.search-result a.cludo-result'):
            url = card.get_attribute('href')
            native_logger.info(f"[Queue] Recording entity: {url}")
            delayed_requests_queue.put(url)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.0)

        try:
            WebDriverWait(driver, TIMEOUT_SEC).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results-section-load-more"))).click()
        except TimeoutException:
            break
    except Exception as ex:
        native_logger.error(f"[Driver] Aborting next crawling due to error: {ex}")
        break

native_logger.info(f"[Queue] Total collected requests: {delayed_requests_queue.qsize()}")

while not delayed_requests_queue.empty():
    url = delayed_requests_queue.get()
    driver.get(url)
    time.sleep(1.0)

    def get_rating():
        el_stars = driver.find_elements(By.CSS_SELECTOR, '#course-page-description i')
        return ";".join([star.get_attribute("class") for star in el_stars])


    record = {
        'title': safe_check_by_selector_text(driver, '#course-page-hero div.title.section h1'),
        'description': safe_check_by_selector_text(driver, '.text-component'),
        'authors': [safe_check_by_selector_text(driver, '.title--alternate > a:nth-child(3)')],
        'rating': get_rating(),
        'votes_count': safe_check_by_selector_text(driver, '.course-sidebar > div:nth-child(1) > div:nth-child(2) > '
                                                           'div:nth-child(2) > span:nth-child(6)'),
        'students_count': None,
        'level': safe_check_by_selector_text(driver, '.course-sidebar div.difficulty-level'),
        'duration': safe_check_by_selector_text(driver, '.course-sidebar > div:nth-child(1) > div:last-child > '
                                                        'div:nth-child(2)'),
        'platform': 'Pluralsight',
        'free': False,
    }

    native_logger.info(f"[Queue] Recording entity: {record}")
    dataframe = dataframe.append(record, ignore_index=True)

dataframe.to_json("pluralsight.json", orient="records")
driver.close()
