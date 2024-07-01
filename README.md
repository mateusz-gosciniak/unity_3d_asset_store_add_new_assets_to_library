# Unity3D AssetStore - Add new assets to library

## Automation Goal
Check if are new free assets and grab these to your asset library on demand

## Business Assumptions 
- 1 User spent once a week time to collect all new free assets (0.05h)  
Current FTE = (0.05 * 4)/160 = 0.00125 FTE

- For first time grabing all existed free assets more than 9000 (11.65h)  
Current FTE = 11.65/160 = 0.073 FTE one-time   
375 [pages] * 111.82 [s per page] = 41932.5 s = 698.875 m = 11.65 h

<i>*(1 FTE == 160 business hours per month)</i>

## Automation Business Value
- Automating boring task
- Collecting asset informations for future analysis 
- Saving FTE = 0.00125 - 0.000675 = <b>0.000575 FTE saving</b> per week
- Saving FTE = 0.073 - 0.064 = <b>0.009 FTE saving</b> one-time

## Processing times
Get all assets from first page from scratch.
- Manual run best time: 1:51.82 
- Automation run time: 1:58.41s - 1:38.15 per asset page

## Automation steps
- Go to Unity3d Asset Store and Login
- Go to page with assets and filter to get only new and free
- Add all assets from page
- Do since all assets will be collected

## Assumptions
Standard User login to Unity without two factor authentication:
- no SSO support,
- no two factor authentication

## Contact:
gosciniak.mateusz@outlook.com

## Stack
Python 3.12.0   
Selenium 4.22.0
