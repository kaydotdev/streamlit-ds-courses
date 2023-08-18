import argparse
import logging
import os
import queue
import sys
import time

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .common import WebDriverContextManager, REQUEST_TIMEOUT, safe_query_text

DOWNLOAD_DELAY = 5.0

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def parse_rating(driver):
    star_elements = driver.find_elements(By.CSS_SELECTOR, '#course-page-description i')
    return ";".join([star.get_attribute("class") for star in star_elements])


def main():
    parser = argparse.ArgumentParser(description="Processing pipeline for raw scraped data.")
    parser.add_argument("--output", type=str, default="pluralsight.json", help="File path to the webcrawling results.")

    args = parser.parse_args()

    df = pd.DataFrame(columns=["title", "description", "authors", "rating", "votes_count", "students_count", "level", "duration", "platform", "free"])
    pages_url_queue = queue.Queue()

    driver_binary_location = os.environ.get("CHROME_DRIVER")

    if driver_binary_location is None:
        logger.error("[Driver] Driver binary location is not defined. Set driver binary path in `CHROME_DRIVER`.")
        sys.exit(1)

    with WebDriverContextManager(binary_location=driver_binary_location) as driver:
        logger.info("[Driver] WebDriver is ready.")

        next_page_available = True
        driver.get("https://www.pluralsight.com/search?q=Data%20Science&categories=course&roles=data-professional")

        while next_page_available:
            scroll_anchor = WebDriverWait(driver, REQUEST_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

            for card in scroll_anchor.find_elements(By.CSS_SELECTOR, 'div.search-result a.cludo-result'):
                url = card.get_attribute('href')
                logger.info(f"[Queue] Recording entity: {url}")
                pages_url_queue.put(url)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, REQUEST_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results-section-load-more"))).click()

        logger.info(f"[Queue] Total collected requests: {pages_url_queue.qsize()}")

        while not pages_url_queue:
            driver.get(pages_url_queue.get())
            time.sleep(DOWNLOAD_DELAY)

            record = {
                'title': safe_query_text(driver, '#course-page-hero div.title.section h1'),
                'description': safe_query_text(driver, '.text-component'),
                'authors': [safe_query_text(driver, '.title--alternate > a:nth-child(3)')],
                'rating': parse_rating(driver),
                'votes_count': safe_query_text(driver, '.course-sidebar > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > span:nth-child(6)'),
                'students_count': None,
                'level': safe_query_text(driver, '.course-sidebar div.difficulty-level'),
                'duration': safe_query_text(driver, '.course-sidebar > div:nth-child(1) > div:last-child > div:nth-child(2)'),
                'platform': 'Pluralsight',
                'free': False,
            }

            logger.info(f"[Queue] Recording entity: {record}")
            df = df.append(record, ignore_index=True)

        df.to_json(args.output, orient="records")


if __name__ == "__main__":
    main()

