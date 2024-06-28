import logging
from time import time, sleep
from subprocess import STDOUT

from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

class ChromeDriver:
    ELEMENT_TIMEOUT = 15  # [s]
    WAIT_FOR_ELEMENT = 0.5  # [s]
    
    def __init__(self, enable_logs=False) -> None:
        # enable logs 
        service = ChromeService(service_args=['--log-level=INFO'], 
                                log_output=STDOUT) \
            if enable_logs else ChromeService()
        # configure chrome engine
        options = ChromeDriver.make_options(enable_logs)
        # make selenium Chrome webbrowser object
        self.chrome = Chrome(options, service)
        self.waiter = WebDriverWait(self.chrome, timeout=__class__.ELEMENT_TIMEOUT)
        logging.info("Chrome initialized complete")

    @staticmethod
    def make_options(enable_logs=False):
        options = ChromeOptions()
        
        # more options:
        # https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
        # https://peter.sh/experiments/chromium-command-line-switches/
        additional_arguments = [
            "incognito",
            "no-sandbox",
            "mute-audio",
            "start-maximized",
            "hide-scrollbars",
            "enable-automation",
            "no-default-browser-check",
            "disable-search-engine-choice-screen",
            "disable-popup-blocking",
            "disable-default-apps",
            "disable-extensions",
            "disable-infobars",
            "disable-notifications",
            "disable-save-password-bubble",
            "disable-translate",
        ]

        if enable_logs:
            additional_arguments.append("log-level=0")
            additional_arguments.append("enable-logging=stdout")

        for arg in additional_arguments:
            options.add_argument(arg)
        
        experimental_options_prefs = {}
        options.add_experimental_option("prefs", experimental_options_prefs)
        return options

    def wait_for_element(self, by: str = By.ID, value: str | None = None) -> WebElement:
        """ Wrapper on selenium method find_element.
        Added wait time checking if element appears. 
        Find an element given a By strategy and locator.

        Constants needed to be setup:
        ELEMENT_TIMEOUT = 15
        WAIT_FOR_ELEMENT = 0.5

        :Usage:
            element = wait_for_element(driver, By.ID, 'foo')

        :rtype: WebElement
        """

        start_time = time()
        web_element = None
        while not web_element:
            try:
                web_element = self.chrome.find_element(by, value)
            except NoSuchElementException as ex:
                if time() - start_time < __class__.ELEMENT_TIMEOUT:
                    sleep(__class__.WAIT_FOR_ELEMENT)
                    continue
                
                logging.error(f"element not found: {ex}")
                raise ex
        return web_element

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.error(f"Chrome Driver Exception: {exc_type}, {exc_val}, {exc_tb}")
        
        if not self or not self.chrome:
            logging.warning("Chrome Driver Object not exist")
        else:
            self.chrome.quit()
            logging.info("Chrome closed")
