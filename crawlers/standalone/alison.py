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

from .common import (
    REQUEST_TIMEOUT,
    WebDriverContextManager,
    safe_query_attribute,
    safe_query_text,
)

PAGES_NUMBER = 2
DOWNLOAD_DELAY = 1.0

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    parser = argparse.ArgumentParser(description="Processing pipeline for raw scraped data.")
    parser.add_argument("--output", type=str, default="alison.json", help="File path to the webcrawling results.")

    args = parser.parse_args()

    df = pd.DataFrame(columns=["title", "description", "authors", "rating", "votes_count", "students_count", "level", "duration", "platform", "free"])
    requests_queue = queue.Queue()

    driver_binary_location = os.environ.get("CHROME_DRIVER")

    if driver_binary_location is None:
        logger.error("[Driver] Driver binary location is not defined. Set driver binary path in `CHROME_DRIVER`.")
        sys.exit(1)

    with WebDriverContextManager(binary_location=driver_binary_location) as driver:
        logger.info("[Driver] WebDriver is ready.")

        for page_id in range(PAGES_NUMBER):
            driver.get(f"https://alison.com/tag/data-science?page={page_id+1}")

            try:
                scroll_anchor_query = EC.presence_of_element_located((By.CSS_SELECTOR, "#mobile-scroll-anchor"))
                scroll_anchor = WebDriverWait(driver, REQUEST_TIMEOUT).until(scroll_anchor_query)
                cards = scroll_anchor.find_elements(By.CSS_SELECTOR, "a.course-block-wrapper.more-info")

                for card in cards:
                    url = card.get_attribute("href")
                    logger.info(f"[Queue] Recording entity: '{url}'.")
                    requests_queue.put(url)

                time.sleep(DOWNLOAD_DELAY)
            except Exception as ex:
                logger.error(f"[Driver] Error while parsing page: '{ex}'.")
                break

        logger.info(f"[Queue] Total collected requests: {requests_queue.qsize()}.")

        while not requests_queue.empty():
            driver.get(requests_queue.get())

            scroll_anchor_query = EC.presence_of_element_located((By.CSS_SELECTOR, ".course-brief-container"))
            scroll_anchor = WebDriverWait(driver, REQUEST_TIMEOUT).until(scroll_anchor_query)

            record = {
                "title": safe_query_text(driver, ".course-brief--title > h1:nth-child(1)"),
                "description": safe_query_text(driver, ".course-brief__headline"),
                "authors": [safe_query_text(driver, "a.publisher:nth-child(6) > span:nth-child(2)")],
                "rating": safe_query_attribute(driver, ".stars", "data-fill"),
                "votes_count": None,
                "students_count": safe_query_text(driver, ".course-brief__right > div:nth-child(2) > ul:nth-child(1) > li:nth-child(2) > div:nth-child(2) > span:nth-child(2)"),
                "level": None,
                "duration": safe_query_text(driver, ".course-brief__right > div:nth-child(2) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(3)"),
                "platform": "Alison",
                "free": False,
            }

            logger.info(f"[Queue] Recording entity: {record}.")
            df = df.append(record, ignore_index=True)

        df.to_json(args.output, orient="records")


if __name__ == "__main__":
    main()

