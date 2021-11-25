import sys
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

TIMEOUT_SEC = 5.0

dataframe = pd.DataFrame(columns=['title', 'description', 'authors', 'rating', 'votes_count',
                                  'students_count', 'level', 'duration', 'platform', 'free'])
requests = pd.read_json("skillshare_header.json", orient="records")

native_logger = logging.getLogger()
native_logger.setLevel(logging.INFO)
native_logger.addHandler(logging.StreamHandler(sys.stdout))


def safe_check_by_selector_text(__driver__, __selector__):
    try:
        return WebDriverWait(__driver__, TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, __selector__))).text
    except TimeoutException:
        return None


try:
    for index, row in requests.iterrows():
        chrome_options = Options()

        native_logger.info("[Driver] Open driver")
        driver = webdriver.Chrome(os.environ['CHROME_DRIVER'])
        native_logger.info("[Driver] Driver is ready")

        row_dict = row.to_dict(dict)
        url = row_dict.pop('url', None)

        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            rating_elements = driver.find_elements(By.CSS_SELECTOR, '.tile.expectations.metric li')
            percentage_elements = driver.find_elements(By.CSS_SELECTOR, '.tile.expectations.metric li .percentage')

            record = {
                **row_dict,
                'description': safe_check_by_selector_text(driver, 'div.description-column'),
                'rating': {rating.get_attribute('data-value'): percentage.text for rating, percentage
                           in zip(rating_elements, percentage_elements)},
                'votes_count': [element.text for element in driver.find_elements(By.CSS_SELECTOR, '#metrics-section '
                                                                                                  '.js-tag-template '
                                                                                                  'span.ss-icon-heart')],
                'level': safe_check_by_selector_text(driver, '.level-text .active')
            }

            native_logger.info(record)
            dataframe = dataframe.append(record, ignore_index=True)
        except Exception as ex:
            native_logger.error(f"[ERROR] {ex}")
        finally:
            native_logger.info("[Driver] Closing driver")
            driver.close()
except Exception as ex:
    native_logger.error(f"Application interrupted: {ex}")
finally:
    dataframe.to_json("skillshare.json", orient="records")
