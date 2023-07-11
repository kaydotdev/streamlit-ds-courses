from typing import Any

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

REQUEST_TIMEOUT = 5.0


def safe_query_text(driver: Chrome, selector: str, default: Any = None) -> str | None:
    try:
        selector_query = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        web_driver_delay_query = WebDriverWait(driver, REQUEST_TIMEOUT).until(selector_query)

        return web_driver_delay_query.text
    except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
        return default


def safe_query_attribute(driver: Chrome, selector: str, attribute: str, default: Any = None) -> str | None:
    try:
        selector_query = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        web_driver_delay_query = WebDriverWait(driver, REQUEST_TIMEOUT).until(selector_query)

        return web_driver_delay_query.get_attribute(attribute)
    except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
        return default

