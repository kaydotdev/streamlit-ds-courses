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


driver.get(f"https://www.edx.org/search?subject=Data%20Analysis%20%26%20Statistics&tab=course")

for page_id in range(14):

    try:
        card_grid = WebDriverWait(driver, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.pgn__card-grid")))

        for card in card_grid.find_elements(By.CSS_SELECTOR, 'a.discovery-card-link'):
            url = card.get_attribute('href')
            native_logger.info(f"[Queue] Recording entity: {url}")
            delayed_requests_queue.put(url)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        WebDriverWait(driver, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav.justify-content-center:nth-child(1) > ul:nth-child("
                                                             "2) > li:nth-child(7) > button:nth-child(1)"))).click()
        time.sleep(1.0)
    except Exception as ex:
        native_logger.error(f"[Driver] Aborting next crawling due to error: {ex}")
        break

native_logger.info(f"[Queue] Total collected requests: {delayed_requests_queue.qsize()}")


while not delayed_requests_queue.empty():
    url = delayed_requests_queue.get()
    driver.get(url)

    record = {
        'title': safe_check_by_selector_text(driver, '.col-md-7 > h1:nth-child(1)'),
        'description': safe_check_by_selector_text(driver, '.col-md-7 > div:nth-child(2) > p:nth-child(1)'),
        'authors': [safe_check_by_selector_text(driver, 'div.col-md-6:nth-child(1) > ul:nth-child(1) > '
                                                        'li:nth-child(1)')],
        'rating': None,
        'votes_count': None,
        'students_count': safe_check_by_selector_text(driver, '#enroll > div:nth-child(1) > div:nth-child(2) > '
                                                              'div:nth-child(1)'),
        'level': safe_check_by_selector_text(driver, 'div.col-md-6:nth-child(1) > ul:nth-child(1) > '
                                                     'li:nth-child(3)'),
        'duration': safe_check_by_selector_text(driver, '.pb-4 > div:nth-child(2)'),
        'platform': 'edX',
        'free': safe_check_by_selector_text(driver, 'div.col-12:nth-child(3) > div:nth-child(2) > '
                                                    'div:nth-child(1)') == "Free",
    }

    native_logger.info(f"[Queue] Recording entity: {record}")
    dataframe = dataframe.append(record, ignore_index=True)

dataframe.to_json("edx.json", orient="records")
driver.close()
