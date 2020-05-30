from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

import time
import getpass
import sys
import os

if __name__ == "__main__":
  sys.path.append("./classes")
  
  from BpmSupreme import BpmSupreme
  from BpmSupreme import Song

  # Prompt for user credentials 
  USERNAME = input("Username: ")
  PASSWORD = getpass.getpass()
  DOWNLOAD_PATH = str()

  while not os.path.isdir(DOWNLOAD_PATH):
    DOWNLOAD_PATH = input("Download file path: ")

  # Set Firefox profile 
  options = Options()
  firefox_profile = FirefoxProfile()
  firefox_profile.set_preference("browser.helperApps.neverAsk.openFile", "true")
  firefox_profile.set_preference("browser.helperApps.neverAsk.saveFile", "true")
  firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mpeg,audio/mp3")
  firefox_profile.set_preference("browser.download.dir", DOWNLOAD_PATH)
  firefox_profile.set_preference("browser.download.folderList", 2)
  firefox_profile.set_preference("browser.download.manager.showWhenStarting", "false")
  firefox_profile.set_preference("browser.download.panel.shown", "false")
  firefox_profile.set_preference("browser.safebrowsing.downloads.enabled", "false")

  # Begin main functionality
  with Firefox(firefox_profile) as driver:        
    # MAIN FUNCTION HERE
    # Log into account
    account = BpmSupreme(driver, USERNAME, PASSWORD, DOWNLOAD_PATH)
    assert account.login()

    with os.scandir(DOWNLOAD_PATH) as entries:
      for entry in entries:
        print("Detected file: {}".format(entry.name))
    if input("Is this correct? (y/n): ") != "y":
      print("Exiting...")

    page_count = input("How many pages of the new releases to download: ")
    account.download_new_releases(int(page_count))