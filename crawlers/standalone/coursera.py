import argparse
import logging
import os
import sys
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .common import safe_query_text, safe_query_attribute

PAGES_NUMBER = 100
DOWNLOAD_DELAY = 1.0

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    parser = argparse.ArgumentParser(description="Processing pipeline for raw scraped data.")
    parser.add_argument("--output", type=str, default="coursera.json", help="File path to the webcrawling results.")

    args = parser.parse_args()

    df = pd.DataFrame(columns=["title", "description", "authors", "rating", "votes_count", "students_count", "level", "duration", "platform", "free"])
    df_meta = pd.DataFrame(columns=["url", "title", "authors", "rating", "votes_count", "students_count", "level", "platform", "free"])

    driver_binary_location = os.environ.get("CHROME_DRIVER")

    if driver_binary_location is None:
        logger.error("[Driver] Driver binary location is not defined. Set driver binary path in `CHROME_DRIVER`.")
        sys.exit(1)

    driver_options = webdriver.ChromeOptions()
    driver_options.binary_location = driver_binary_location
    driver = webdriver.Chrome(options=driver_options)

    logger.info("[Driver] WebDriver is ready.")

    for i in range(PAGES_NUMBER):
        driver.get(f"https://www.coursera.org/search?index=prod_all_launched_products_term_optimization&topic=Data%20Science&page={i + 1}")

        try:
            courses_page = WebDriverWait(driver, DOWNLOAD_DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ais-InfiniteHits-list")))

            for course in courses_page.find_elements(By.CSS_SELECTOR, "li.ais-InfiniteHits-item"):
                record_base = {
                    "url": safe_query_attribute(course, "a.result-title-link", "href"),
                    "title": safe_query_text(course, "h2.card-title"),
                    "authors": [safe_query_text(course, "span.partner-name")],
                    "rating": safe_query_text(course, "span.ratings-text"),
                    "votes_count": safe_query_text(course, "span.ratings-count span"),
                    "students_count": safe_query_text(course, "div.enrollment span.enrollment-number"),
                    "level": safe_query_text(course, "span.difficulty"),
                    "platform": "Coursera",
                    "free": False
                }

                logger.info(f"[Queue] Recording entity: {record_base}")
                df_meta = df_meta.append(record_base, ignore_index=True)
        except Exception as ex:
            logger.error(f"[Driver] Aborting next crawling due to error: {ex}")

    driver.close()

    for _, row in df_meta.iterrows():
        row_dict = row.to_dict()
        url = row_dict.pop("url", None)

        if url is None:
            logger.warn("[Driver] Failed to parse URL. Skipping...")

        driver.get(str(url))

        try:
            record_base = {
                **row_dict,
                "description": safe_query_text(driver, ".max-text-width"),
                "duration": safe_query_text(driver, "div._cs3pjta:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(2)")
            }

            logger.info(f"[Driver] Recording entity: {record_base}")
            df = df.append(record_base, ignore_index=True)

            time.sleep(DOWNLOAD_DELAY)
        except Exception as ex:
            logger.error(f"Failed to add new record to the dataframe_meta: {ex}.")

    df.to_json(args.output, orient="records")

    driver.close()

