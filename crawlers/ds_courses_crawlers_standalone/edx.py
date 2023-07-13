import argparse
import logging
import os
import queue
import sys
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .common import REQUEST_TIMEOUT, safe_query_text

PAGES_NUMBER = 14
DOWNLOAD_DELAY = 1.0


def main():
    parser = argparse.ArgumentParser(description="Processing pipeline for raw scraped data.")
    parser.add_argument("--output", type=str, default="../../data/edx.json", help="File path to the webcrawling results.")

    args = parser.parse_args()

    df_columns = ['title', 'description', 'authors', 'rating', 'votes_count', 'students_count', 'level', 'duration', 'platform', 'free']
    df = pd.DataFrame(columns=df_columns)

    pages_url_queue = queue.Queue()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    driver_binary_location = os.environ.get('CHROME_DRIVER')

    if driver_binary_location is None:
        logger.error("[Driver] Driver binary location is not defined. Set driver binary path in `CHROME_DRIVER`.")
        sys.exit(1)

    driver_options = webdriver.ChromeOptions()
    driver_options.binary_location = driver_binary_location
    driver = webdriver.Chrome(options=driver_options)

    logger.info("[Driver] WebDriver is ready.")


    for page_id in range(PAGES_NUMBER):
        try:
            card_grid_selector = EC.presence_of_element_located((By.CSS_SELECTOR, "div.pgn__card-grid"))
            card_grid = WebDriverWait(driver, REQUEST_TIMEOUT).until(card_grid_selector)

            for card in card_grid.find_elements(By.CSS_SELECTOR, 'a.discovery-card-link'):
                url = card.get_attribute('href')

                logger.info(f"[Driver] Page '{url}' put into a queue.")
                pages_url_queue.put(url)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            next_page_button_selector = EC.presence_of_element_located((By.CSS_SELECTOR, "nav.justify-content-center:nth-child(1) > ul:nth-child(2) > li:nth-child(7) > button:nth-child(1)"))
            next_page_button = WebDriverWait(driver, REQUEST_TIMEOUT).until(next_page_button_selector)
            next_page_button.click()

            time.sleep(DOWNLOAD_DELAY)

        except Exception as ex:
            logger.error(f"Failed to parse a page number {page_id}: {ex}.")

    logger.info(f"[Queue] Total collected requests: {pages_url_queue.qsize()}")

    while not pages_url_queue.empty():
        driver.get(str(pages_url_queue.get()))

        record = {
            'title': safe_query_text(driver, '.col-md-7 > h1:nth-child(1)'),
            'description': safe_query_text(driver, '.col-md-7 > div:nth-child(2) > p:nth-child(1)'),
            'authors': [safe_query_text(driver, 'div.col-md-6:nth-child(1) > ul:nth-child(1) > li:nth-child(1)')],
            'rating': None,
            'votes_count': None,
            'students_count': safe_query_text(driver, '#enroll > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)'),
            'level': safe_query_text(driver, 'div.col-md-6:nth-child(1) > ul:nth-child(1) > li:nth-child(3)'),
            'duration': safe_query_text(driver, '.pb-4 > div:nth-child(2)'),
            'platform': 'edX',
            'free': safe_query_text(driver, 'div.col-12:nth-child(3) > div:nth-child(2) > div:nth-child(1)') == "Free"
        }

        logger.info(f"[Driver] Writing new record: {record}.")
        df = df.append(record, ignore_index=True)

    df.to_json(args.output, orient="records")
    driver.close()

