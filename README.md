# unity_3d_asset_store_add_new_assets_to_library

Automation project which lookup Unity3D asset store to find assets which wasn't attached to your account and added it to your account.


Stack: Python 3.12.0, 
Libs: Requests, BeautifulSoup4, Selenium

Automation Goal: Check on demand if new assets appears and add it to your account 
Optionaly Goal: Make Database with your assets, and provide additional informations there  

Automation steps:
- Open Chrome
- Go to Unity3d Asset Store
- Login
- Go to Page with assets packages
- Choose filters to get only free assets which were not purchased
- Go through finded assets per page
- Get asset in first row and first column
- Check if option "Add to My Assets" exists
- if option exists:
    - Click on it
    - Wait for "License" popup
    - Wait for "Added to My Assets" popup 
    - Refresh page
- if not exists:
    - go to next column or row up to last one

