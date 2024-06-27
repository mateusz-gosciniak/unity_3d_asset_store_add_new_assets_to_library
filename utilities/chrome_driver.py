import logging
from subprocess import STDOUT

from selenium.webdriver import Chrome, ChromeOptions, ChromeService


class ChromeDriver:
    def __init__(self, enable_logs=False) -> None:
        # enable logs 
        service = ChromeService(service_args=['--log-level=INFO'], 
                                log_output=STDOUT) \
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
