""" File which run automation to grab new free assets from Unity 3D Store. """

# python standard packages
import logging 

# third-party packages
# import bs4
# import requests
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# in project packages
from utilities.chrome_driver import ChromeDriver


# logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# project constants
ELEMENT_TIMEOUT = 2  # [s]


def run_automation():
    # STEP 1 - Open Chrome
    with ChromeDriver() as chrome_driver:
        selenium_waiter = WebDriverWait(chrome_driver, timeout=ELEMENT_TIMEOUT)

        # STEP 2 - Open Asset Store Page
        chrome_driver.get("https://assetstore.unity.com/")
        logging.info("Asset Store open")
        accept_all_cookies_btn = chrome_driver.find_element(By.ID, "onetrust-accept-btn-handler")
        selenium_waiter.until(EC.element_to_be_clickable(accept_all_cookies_btn))
        accept_all_cookies_btn.click()
        logging.info("Cookies Accepted")
        # user_login_button
        # User interaction only in case of debug
        input("press key")


def main():
    logging.info("=== START ===")
    try:
        logging.info("Automation started...")
        run_automation()
    except Exception as ex:
        logging.error(f"During automation unhandled exception occured: {ex}")
        logging.error("Automation failed")
    else:
        logging.info("Automation finished with success")
    finally:
        logging.info("=== END ===")


if __name__ == "__main__":
    main()
