""" File which run automation to grab new free assets from Unity 3D Store. """

import logging
import subprocess

import bs4
import requests
from selenium.webdriver import Chrome, ChromeOptions, ChromeService


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChromeDriver:
    def __init__(self, enable_logs=False) -> None:
        # enable logs 
        service = ChromeService(service_args=['--log-level=INFO'], 
                                log_output=subprocess.STDOUT) \
            if enable_logs else ChromeService()
        # configure chrome engine
        options = ChromeDriver.make_options(enable_logs)
        # make selenium Chrome webbrowser object
        self.chrome_driver = Chrome(options, service)
        logging.info("Chrome init complete")

    @staticmethod
    def make_options(enable_logs=False):
        options = ChromeOptions()
        
        # more options:
        # https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
        # https://peter.sh/experiments/chromium-command-line-switches/
        additional_arguments = [
            "incognito",
            "start-maximized",
            "disable-popup-blocking",
            "disable-default-apps",
            "disable-extensions",
            "enable-automation",
            "no-sandbox",
            "disable-infobars",
            "disable-notifications",
            "disable-save-password-bubble",
            "disable-translate",
            "mute-audio",
            "hide-scrollbars",
            "no-default-browser-check",
            "disable-search-engine-choice-screen",
        ]

        if enable_logs:
            additional_arguments.append("log-level=0")
            additional_arguments.append("enable-logging=stdout")

        for arg in additional_arguments:
            options.add_argument(arg)
        
        experimental_options_prefs = {}
        options.add_experimental_option("prefs", experimental_options_prefs)
        return options

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
