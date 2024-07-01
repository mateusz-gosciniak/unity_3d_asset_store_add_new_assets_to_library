""" File which run automation to grab new free assets from Unity 3D Store. """

# python standard packages
import logging
import os
import sys
import time
import traceback
from pathlib import Path
from re import compile
from datetime import datetime

# third-party packages
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from pyautogui import screenshot

# in project packages
from utilities.asset_store_wrapper import AssetStoreWrapper, AssetStoreAssetButtonError
from project_settings import ProjectSettings


class UnrecognizedAssetStatusError(Exception):
    pass


class AutomationAddNewFreeAssetsToLib():
    def __init__(self, unity_credentials, log_folder_path) -> None:
        self.unity_credentials = unity_credentials
        self.added_assets = []
        self.general_exception_count = 0
        self.intercepted_exception_count = 0
        self.log_folder_path = log_folder_path

    def _get_assets_count(self, asset_store):
        # Get how many results is on page
        results_text_xpath = "//div[text()[contains(.,'results')]]"
        results_div = asset_store.chrome.find_element(By.XPATH, results_text_xpath)
        results_text = results_div.text

        # Pattern to find 3 groups of numbers in string ex. 1-24 of 104 results
        regex_pattern = compile(r'(\d+)-(\d+) of (\d+)')
        regex_match = regex_pattern.match(results_text)
        if not regex_match:
            raise Exception("No assets to add")

        if len(regex_match.groups()) != 3:
            raise Exception("No assets to add")

        # Geting last number as total amount of results
        avaiable_assets = int(regex_match.group(3))
        return avaiable_assets

    def _collect_asset_info(self, asset_web_element):
        asset_string = ','.join(asset_web_element.text.split('\n'))
        self.added_assets.append(asset_string)
        logging.info(f"Asset to add: {asset_string}")

    def _get_assets_per_page(self, asset_store):
        # Refresh page
        asset_store.open_free_not_added_assets()
        
        # Get avaiable assets info
        avaiable_assets = self._get_assets_count(asset_store)
        assets = asset_store.get_assets_from_page_as_collection()
        if assets is None:
            logging.info(f"After page refreshing no more assets found")
            return True  # end of processing
        logging.info(f"Assets count: {avaiable_assets}, on this page is {len(assets)}")

        # Iter by founded assets
        for asset in assets:
            # Check asset status
            asset_status = asset_store.get_asset_status(asset).lower().strip()

            # Check if more assets waits
            if asset_status == "Request access".lower().strip():
                logging.info(f"After page refreshing no more assets found")
                return True  # end of processing
            
            # Check if status downloaded go to next
            if asset_status == "Open in Unity".lower().strip():
                continue
            
            # Check if assets possible to add
            if asset_status != "Add to My Assets".lower().strip():
                raise UnrecognizedAssetStatusError("Unrecognized Asset Status")

            # Add asset to account
            try:
                asset_store.add_asset(asset)
            except AssetStoreAssetButtonError as ex:
                logging.info(f"Something goes wrong with this asset during adding: {ex}")
                return False
            except ElementClickInterceptedException as ex:
                if self.intercepted_exception_count == 3:
                    raise Exception("ElementClickInterceptedException 3 times in a row") from ex    
                self.intercepted_exception_count += 1 
                logging.info(f"Something goes wrong with this asset during adding: {ex}")
                return False
            except Exception as ex:
                if self.general_exception_count == 3:
                    raise ex
                self.general_exception_count += 1
                logging.info(f"Something goes wrong with this asset during adding: {ex}")
                return False
            else:
                # Reset exception counters
                self.general_exception_count = 0
                self.intercepted_exception_count = 0

                # Add info about assets
                self._collect_asset_info(asset)

        logging.info("Page finished - refreshing")
        return False

    def _make_screen(self, asset_store):
        # 1st Screen Making try
        log_screen_path = os.path.join(self.log_folder_path, "screen_log.png")
        screen_done = False
        try:
            asset_store.chrome.save_screenshot(log_screen_path)
            screen_done = True
        except Exception as ex:
            logging.error(f"Error during makeing screen: {ex}")
        # 2nd Screen Making try if before fail
        if not screen_done:
            logging.info("Making screen second try")
            try:
                screenshot(log_screen_path)
            except Exception as ex:
                logging.error(f"Error during makeing screen 2nd time: {ex}")
                logging.info("No screen avaiable")

    def run(self):
        with AssetStoreWrapper() as asset_store:
            try:
                asset_store.login_to_asset_store(self.unity_credentials)
                page_start_time = time.time()
                while not self._get_assets_per_page(asset_store):
                    logging.info(f"Found more assets - page refreshing")
                    page_end_time = time.time() - page_start_time
                    logging.info(f"time to get asset from page take: {page_end_time}s")
                logging.info("All Assets Processed and should be added to account")
            except Exception as main_ex:
                logging.error(f"Error during processing automation: {main_ex}")
                self._make_screen(asset_store)
                raise main_ex


def main():    
    # make folder
    log_folder = "logs"
    date_timestamp = datetime.now().strftime("%H_%M_%S__%m_%d_%Y")
    log_folder_name = f"run_{date_timestamp}"
    log_folder_path = Path(os.path.join('.', log_folder, log_folder_name)).absolute()
    os.makedirs(log_folder_path, exist_ok=True)

    # create log file
    date_timestamp = datetime.now().strftime("%H_%M_%S__%m_%d_%Y")
    log_file_name = f"{Path(sys.argv[0]).stem}.log"  # argv[0] is the script name 
    log_file_path = os.path.join(log_folder_path, log_file_name)
    
    # logging configuration
    logging.basicConfig(filename=log_file_path,
                        level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # preapare credentials
    unity_credentials = (ProjectSettings.UNITY_CREDENTIALS_NAME, ProjectSettings.UNITY_CREDENTIALS_EMAIL)

    logging.info("=== START ===")
    
    automation = None
    try:
        automation_start_time = time.time()
        logging.info("Automation started...")
        automation = AutomationAddNewFreeAssetsToLib(unity_credentials, log_folder_path)
        automation.run()  # <-- entry point
    except Exception as ex:
        logging.error(f"During automation unhandled exception occured: {ex}, traceback: {traceback.format_exc()}")
        logging.error("Automation failed")
    else:
        logging.info("Automation finished with success")
    finally:
        if automation:
            logging.info(f"Added {len(automation.added_assets)} assets.")
            logging.info(f"Please check details of added assets: \n{automation.added_assets}")
            
        automation_end_time = time.time() - automation_start_time
        logging.info(f"Automation take: {automation_end_time}s")
        logging.info("=== END ===")


if __name__ == "__main__":
    main()
