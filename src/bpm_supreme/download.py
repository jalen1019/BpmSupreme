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
from os import path
from os import listdir

from classes import BpmSupreme

# Prompt for user credentials 
USERNAME = input("Username:")
PASSWORD = getpass.getpass()
DOWNLOAD_PATH = str()

while not path.isdir(DOWNLOAD_PATH):
  DOWNLOAD_PATH = input("Download file path: ")

# Set Firefox profile 
options = Options()
firefox_profile = FirefoxProfile()
firefox_profile.set_preference("browser.helperApps.neverAsk.openFile", "true")
firefox_profile.set_preference("browser.helperApps.neverAsk.saveFile", "true")
firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "true")
firefox_profile.set_preference("browser.download.dir", DOWNLOAD_PATH)
firefox_profile.set_preference("browser.download.folderList", 2)
firefox_profile.set_preference("browser.download.manager.showWhenStarting", "false")
firefox_profile.set_preference("browser.download.panel.shown", "false")
firefox_profile.set_preference("browser.safebrowsing.downloads.enabled", "false")

with Firefox(firefox_profile) as driver:        
  # MAIN FUNCTION HERE
  # Log into account
  account = BpmSupreme.BpmSupreme(driver, USERNAME, PASSWORD)
  account.site_login()

  input("Press ENTER to begin downloading library...")
  account.download_library()
