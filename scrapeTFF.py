import os
import time
import datetime
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Instantiate an Options object
# and add the “ — headless” argument
opts = Options()
opts.add_argument(" — headless")
# Don't load images to reduce load. This is browser specific.
chrome_prefs = {}
opts.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

# If necessary set the path to you browser’s location
opts.binary_location= "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

# Set the location of the webdriver
chrome_driver = os.getcwd() +"\\chromedriver.exe"

# Instantiate a webdriver
driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)

# DataFrame for scraped data
  
df = pd.DataFrame(
         {
         "username": [],
         "postdate": [],
         "posttime": [],
         }
)

# Loop through pages to scrape using page numbers. 
i=0 # starting page
while True:
     i += 2 # we can increase the page number immediately by 2 as the two pages above are dynamically loaded
     if i >= 1047: # 1047 is the last page in the thread used below
         break
     driver.get("https://tff-forum.de/t/tsla-aktie-tesla-inc-bis-11-02-2021/1069?page="+str(i))
     
     # Put the page source into a variable and create a BS object from it
     soup_file=driver.page_source
     soup = BeautifulSoup(soup_file, features="lxml")
  
     # find all 
     posts = soup.find_all("div", "topic-meta-data")
  
     # extract data for each row and add it to DataFrame
     for post in posts:
     
         usercard = post.next_element.next_element.next_element
         username = usercard.get("data-user-card")
  
         postinfo = post.find_next("a", "post-date")
         postdateINT = int(postinfo.next_element.get("data-time"))/1000
         postdatetime = datetime.datetime.fromtimestamp(postdateINT)
  
         dftemp = pd.DataFrame(
                 {
                 "username": [str(username)],
                 "postdate": [postdatetime.date()],
                 "posttime": [postdatetime.time()],
                 }
         )
  
         df = pd.concat([df,dftemp], ignore_index=True, sort=False)
         df.to_csv("tff_aktien.csv") # save to file each cycle just in case browser freezes
  
# Close the browser
driver.quit()

# count how many times a date appears
dfc = df["postdate"].value_counts().rename_axis("countdates").reset_index(name="counts")
df = pd.concat([df, dfc.reindex(df.index)], axis=1)

# save to csv file with current date
dt = datetime.datetime.now()
df.to_csv(dt.strftime("%Y")+"-"+dt.strftime("%m")+"-"+dt.strftime("%d")+"-"+"tff_aktien.csv")