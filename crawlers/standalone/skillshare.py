import argparse
import logging
import os
import sys

import pandas as pd
from selenium.webdriver.common.by import By

from .common import WebDriverContextManager, safe_query_text

DOWNLOAD_DELAY = 5.0

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    parser = argparse.ArgumentParser(description="Processing pipeline for raw scraped data.")
    parser.add_argument("--output", type=str, default=".data/skillshare.json", help="File path to the webcrawling results.")

    args = parser.parse_args()

    df = pd.DataFrame(columns=["title", "description", "authors", "rating", "votes_count", "students_count", "level", "duration", "platform", "free"])
    df_meta = pd.DataFrame(columns=["url", "title", "authors", "rating", "votes_count", "students_count", "level", "platform", "free"])

    driver_binary_location = os.environ.get("CHROME_DRIVER")

    if driver_binary_location is None:
        logger.error("[Driver] Driver binary location is not defined. Set driver binary path in `CHROME_DRIVER`.")
        sys.exit(1)

    for _, row in df_meta.iterrows():
        with WebDriverContextManager(binary_location=driver_binary_location) as driver:
            logger.info("[Driver] WebDriver is ready.")

            row_data = row.to_dict(dict)
            url = row_data.pop("url", None)

            if url is None:
                continue

            driver.get(url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            rating_elements = driver.find_elements(By.CSS_SELECTOR, ".tile.expectations.metric li")
            percentage_elements = driver.find_elements(By.CSS_SELECTOR, ".tile.expectations.metric li .percentage")

            record = {
                **row_data,
                "description": safe_query_text(driver, "div.description-column"),
                "rating": { rating.get_attribute("data-value"): percentage.text for rating, percentage in zip(rating_elements, percentage_elements, strict=True) },
                "votes_count": [element.text for element in driver.find_elements(By.CSS_SELECTOR, "#metrics-section .js-tag-template span.ss-icon-heart")],
                "level": safe_query_text(driver, ".level-text .active")
            }

            logger.info(f"[Queue] Recording entity: {record}")
            df = df.append(record, ignore_index=True)

        df.to_json(args.output, orient="records")


if __name__ == "__main__":
    main()

