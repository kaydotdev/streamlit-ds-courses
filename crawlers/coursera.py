import sys
import logging
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

TIMEOUT_SEC = 1

native_logger = logging.getLogger()
native_logger.setLevel(logging.INFO)
native_logger.addHandler(logging.StreamHandler(sys.stdout))

native_logger.info("[Driver] Initiating driver")
driver = webdriver.Chrome(os.environ['CHROME_DRIVER'])
native_logger.info("[Driver] Driver is ready")

dataframe_full = pd.DataFrame(columns=['title', 'description', 'authors', 'rating', 'votes_count',
                                       'students_count', 'level', 'duration', 'platform', 'free'])
dataframe = pd.read_json("coursera_header.json", orient="records")


def safe_check_by_selector_text(__driver__, __selector__):
    try:
        return WebDriverWait(__driver__, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, __selector__))).text
    except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
        return None


for index, row in dataframe.iterrows():
    row_dict = row.to_dict(dict)
    url = row_dict.pop('url', None)

    driver.get(url)
    product_glance_element = safe_check_by_selector_text(driver, 'div.ProductGlance div._1tu07i3a')

    try:
        record_base = {
            **row_dict,
            'description': safe_check_by_selector_text(driver, '.max-text-width'),
            'duration': safe_check_by_selector_text(driver, 'div._cs3pjta:nth-child(1) > div:nth-child(1) > '
                                                            'div:nth-child(5) > div:nth-child(2)')
        }
        native_logger.info(f"[Queue] Recording entity: {record_base}")
        dataframe_full = dataframe_full.append(record_base, ignore_index=True)
    except Exception as ex:
        native_logger.error(f"[ERROR] {ex}")

dataframe_full.to_json("coursera.json", orient="records")
driver.close()
