import argparse
import logging
import os
import sys

import pandas as pd
from selenium import webdriver

from .common import safe_query_text

PAGES_NUMBER = 2
DOWNLOAD_DELAY = 1.0


def main():
    parser = argparse.ArgumentParser(description="Processing pipeline for raw scraped data.")
    parser.add_argument("--input", type=str, default="../../data/coursera_meta.json", help="File path to the Coursera courses metadata.")
    parser.add_argument("--output", type=str, default="../../data/coursera.json", help="File path to the webcrawling results.")

    args = parser.parse_args()

    dataframe = pd.DataFrame(columns=['title', 'description', 'authors', 'rating', 'votes_count', 'students_count', 'level', 'duration', 'platform', 'free'])
    dataframe_meta = pd.read_json(args.input, orient="records")

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

    for _, row in dataframe_meta.iterrows():
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
            dataframe = dataframe.append(record_base, ignore_index=True)
        except Exception as ex:
            logger.error(f"Failed to add new record to the dataframe_meta: {ex}.")

    dataframe.to_json(args.output, orient="records")

    driver.close()

