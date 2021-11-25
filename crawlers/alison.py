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


for page_id in range(2):
    driver.get(f"https://alison.com/tag/data-science?page={page_id+1}")

    try:
        scroll_anchor = WebDriverWait(driver, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mobile-scroll-anchor")))

        for card in scroll_anchor.find_elements(By.CSS_SELECTOR, 'a.course-block-wrapper.more-info'):
            url = card.get_attribute('href')
            native_logger.info(f"[Queue] Recording entity: {url}")
            delayed_requests_queue.put(url)

        time.sleep(1.0)
    except Exception as ex:
        native_logger.error(f"[Driver] Aborting next crawling due to error: {ex}")
        break

native_logger.info(f"[Queue] Total collected requests: {delayed_requests_queue.qsize()}")


while not delayed_requests_queue.empty():
    url = delayed_requests_queue.get()
    driver.get(url)

    scroll_anchor = WebDriverWait(driver, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.course-brief-container')))

    record = {
        'title': safe_check_by_selector_text(driver, '.course-brief--title > h1:nth-child(1)'),
        'description': safe_check_by_selector_text(driver, '.course-brief__headline'),
        'authors': [safe_check_by_selector_text(driver, 'a.publisher:nth-child(6) > span:nth-child(2)')],
        'rating': safe_check_by_selector_attr(driver, '.stars', 'data-fill'),
        'votes_count': None,
        'students_count': safe_check_by_selector_text(driver, '.course-brief__right > div:nth-child(2) > '
                                                              'ul:nth-child(1) > li:nth-child(2) > div:nth-child(2) >'
                                                              ' span:nth-child(2)'),
        'level': None,
        'duration': safe_check_by_selector_text(driver, '.course-brief__right > div:nth-child(2) > ul:nth-child(1) > '
                                                        'li:nth-child(1) > span:nth-child(3)'),
        'platform': 'Alison',
        'free': False,
    }

    native_logger.info(f"[Queue] Recording entity: {record}")
    dataframe = dataframe.append(record, ignore_index=True)

dataframe.to_json("alison.json", orient="records")
driver.close()
