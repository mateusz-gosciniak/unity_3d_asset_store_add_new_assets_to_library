""" File which run automation to grab new free assets from Unity 3D Store. """

# python standard packages
import logging
import traceback
from re import compile

# third-party packages
from selenium.webdriver.common.by import By

# in project packages
from utilities.asset_store_wrapper import AssetStoreWrapper
from project_settings import ProjectSettings


class AutomationAddNewFreeAssetsToLib():
    def __init__(self, unity_credentials) -> None:
        self.unity_credentials = unity_credentials
        self.added_assets = []

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
            # Add info about assets
            self._collect_asset_info(asset)

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
            asset_store.add_asset(asset)

        logging.info(f"Page finished - refreshing")
        return False

    def run(self):
        with AssetStoreWrapper() as asset_store:
            asset_store.login_to_asset_store(self.unity_credentials)
            while not self._get_assets_per_page(asset_store):
                logging.info(f"Found more assets - page refreshing")
                break
            logging.info("All Assets Processed and should be added to account")
            logging.info(f"Please check added assets: {self.added_assets}")


def main():
    # logging configuration
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    unity_credentials = (ProjectSettings.UNITY_CREDENTIALS_NAME, ProjectSettings.UNITY_CREDENTIALS_EMAIL)

    logging.info("=== START ===")
    try:
        logging.info("Automation started...")
        AutomationAddNewFreeAssetsToLib(unity_credentials).run()  # <-- entry point
    except Exception as ex:
        logging.error(f"During automation unhandled exception occured: {ex}, traceback: {traceback.format_exc()}")
        logging.error("Automation failed")
    else:
        logging.info("Automation finished with success")
    finally:
        logging.info("=== END ===")


if __name__ == "__main__":
    main()
