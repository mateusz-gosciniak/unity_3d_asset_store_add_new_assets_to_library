""" File which run automation to grab new free assets from Unity 3D Store. """

import logging

import bs4
import requests
from selenium.webdriver import Chrome, ChromeOptions


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChromeDriver:
    def __init__(self) -> None:
        options = ChromeOptions()
        additional_arguments = [
            "start-maximized"
        ]
        for arg in additional_arguments:
            options.add_argument(arg)

        self.chrome_driver = Chrome(options)
        logging.info("Chrome init complete")

    def __enter__(self):
        return self.chrome_driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.error(f"Chrome Driver Exception: {exc_type}, {exc_val}, {exc_tb}")
        
        if not self or not self.chrome_driver:
            logging.warning("Chrome Driver Object not exist")
        else:
            self.chrome_driver.quit()
            logging.info("Chrome closed")


def run_automation():
    # STEP 1 - Open Chrome
    with ChromeDriver() as chrome_driver:
        # STEP 2 - Open Asset Store Page
        chrome_driver.get("https://assetstore.unity.com/")
        logging.info("Asset Store open")

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
