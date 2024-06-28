# python standard packages
import logging
from time import sleep

# third-party packages
import keyring
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# in project packages
from utilities.chrome_driver import ChromeDriver


class AssetStoreBadCredentialsError(Exception):
    pass


class AssetStoreWrongPageError(Exception):
    pass


class AssetStoreAssetButtonError(Exception):
    pass


class AssetStoreWrapper(ChromeDriver):
    ASSET_STORE_URL = "https://assetstore.unity.com"
    ASSET_STORE_LOGIN_URL = f"{ASSET_STORE_URL}/auth/login"
    ASSET_STORE_DESCRIPTION = "Unity Asset Store - The Best Assets"

    def open_main_page(self, query_parameters=""):
        self.chrome.get(f"{__class__.ASSET_STORE_URL}{query_parameters}")
        logging.info("Asset Store open")

    def accept_cookies(self):
        cookies_btn_id = "onetrust-accept-btn-handler"
        accept_all_cookies_btn = self.wait_for_element(By.ID, cookies_btn_id)
        self.waiter.until(EC.element_to_be_clickable(accept_all_cookies_btn))
        accept_all_cookies_btn.click()
        logging.info("Cookies accepted")

    def open_login_page(self):
        login_query_param = "?redirect_to=%2F"
        self.chrome.get(f"{__class__.ASSET_STORE_LOGIN_URL}{login_query_param}")
        logging.info("Login Page open")
        return self.chrome.current_url

    def input_email_login_page(self, unity_account_email):
        email_field_id = "conversations_create_session_form_email"
        email_field = self.wait_for_element(By.ID, email_field_id)
        self.waiter.until(EC.element_to_be_clickable(email_field))
        email_field.send_keys(unity_account_email)
        logging.info("Email filled")

    def input_password_login_page(self, credentials):
        password_field_id = "conversations_create_session_form_password"
        password_field = self.wait_for_element(By.ID, password_field_id)
        self.waiter.until(EC.element_to_be_clickable(password_field))
        password_field.send_keys(keyring.get_password(*credentials))
        logging.info("Password filled")

    def submit_login_page(self):
        submit_btn_xpath = "//input[@type='submit']"
        submit_btn = self.wait_for_element(By.XPATH, submit_btn_xpath)
        self.waiter.until(EC.element_to_be_clickable(submit_btn))
        submit_btn.click()
        logging.info("Form Submited")

    def login_to_asset_store(self, unity_credentials):
        self.open_main_page()
        self.accept_cookies()
        login_page_url = self.open_login_page()
        self.input_email_login_page(unity_credentials[1])
        self.input_password_login_page(unity_credentials)
        self.submit_login_page()
        
        # check if next page appear and if credentials are valid
        if not __class__.ASSET_STORE_DESCRIPTION.lower() in self.chrome.page_source.lower():
            if self.chrome.current_url.lower() == login_page_url.lower():
                raise AssetStoreBadCredentialsError("Bad Credentials")
            else:
                raise AssetStoreWrongPageError("Wrong Page obtained after login, maybe 2FA enabled?")
        logging.info("Asset Store sign in")

    def open_free_not_added_assets(self):
        free_assets = "free=true"
        exclude_added = "exclude=true"
        order_by_one = "orderBy=1"
        query_string_parameters = f"?{free_assets}&{exclude_added}&{order_by_one}"
        self.open_main_page(query_string_parameters)
        logging.info("Asset Store filtered by free to download")

    def get_assets_from_page_as_collection(self):
        # Find table of assets
        asset_grid = self.wait_for_element(By.XPATH, "//div[@data-test='asset-grid']/div")
        self.waiter.until(EC.element_to_be_clickable(asset_grid))
        if not "Add to My Assets" in asset_grid.text:
            return

        # Get assets as collections
        assets = asset_grid.find_elements(By.XPATH, "./div")
        if len(assets) == 0:
            return
        return assets
    
    def get_asset_button(self, asset_web_element):
        buttons = asset_web_element.find_elements(By.XPATH, ".//button[*]")
        if buttons is None:
            raise AssetStoreAssetButtonError("Button not found")
        
        if len(buttons) != 2:
            raise AssetStoreAssetButtonError("Button not found")
            
        _, asset_btn = buttons  # unpack, and discar add to favorite button
        return asset_btn  # can be open in unity, add to assets etc.

    def get_asset_status(self, asset_web_element):
        asset_btn = self.get_asset_button(asset_web_element)
        if asset_btn is None:
            raise AssetStoreAssetButtonError("Button not found")

        return asset_btn.text
    
    def add_asset(self, asset_web_element):
        add_asset_btn = self.get_asset_button(asset_web_element)  # assumption
        if add_asset_btn is None:
            raise AssetStoreAssetButtonError("Button not found")

        add_asset_btn.click()
        logging.info(f"Add asset clicked")

        accept_btn_xpath = "//button[@label='Accept']"
        accept_btn = self.wait_for_element(By.XPATH, accept_btn_xpath)
        self.waiter.until(EC.element_to_be_clickable(accept_btn))
        accept_btn.click()
        logging.info(f"Accept button clicked")
        
        # Added to My Assets Popup check
        added_popup_xpath = "//div[text()[contains(.,'Added to My Assets')]]"
        added_popup = self.wait_for_element(By.XPATH, added_popup_xpath)
        self.waiter.until(EC.element_to_be_clickable(added_popup))
        logging.info(f"Added to My Assets Popup appear")
        
        # close popup by sending Escape key
        sleep(1)
        ActionChains(self.chrome).send_keys(Keys.ESCAPE).perform()
        logging.info(f"Send ESC to close popup")
