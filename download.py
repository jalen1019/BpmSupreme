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

# Prompt for user credentials 
USERNAME = input("Username:")
PASSWORD = getpass.getpass()
SLEEP_INTERVAL = 1.5

# Set Firefox profile 
options = Options()
firefox_profile = FirefoxProfile()
firefox_profile.set_preference("browser.helperApps.neverAsk.openFile", "true")
firefox_profile.set_preference("browser.helperApps.neverAsk.saveFile", "true")
firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "true")
firefox_profile.set_preference("browser.download.dir", "/home/jalen/Music/bpm_supreme")
firefox_profile.set_preference("browser.download.folderList", 2)
firefox_profile.set_preference("browser.download.manager.showWhenStarting", "false")
firefox_profile.set_preference("browser.download.panel.shown", "false")
firefox_profile.set_preference("browser.safebrowsing.downloads.enabled", "false")

with Firefox(firefox_profile) as driver:
  def load_page():
    try:
      WebDriverWait(driver, 10).until(expected_conditions.invisibility_of_element_located(driver.find_element_by_xpath("//div[@class='loader']")))

    except NoSuchElementException:
      print("Exception Occurred! Waiting " + str(SLEEP_INTERVAL) + " seconds before resuming...")
      time.sleep(SLEEP_INTERVAL)

  def site_login(USERNAME, PASSWORD):
    # Get the initial site page
    driver.get("https://www.bpmsupreme.com/")

    # Click on login box at top of page
    load_page()
    login_box = driver.find_element_by_class_name("user-login-logout")
    login_box.click()

    # Initialize username and password field variables
    load_page()
    user_name_box = driver.find_element_by_id("login-form-email")
    pass_box = driver.find_element_by_id("login-form-password")

    # Input user credentials
    user_name_box.send_keys(USERNAME + Keys.TAB)
    pass_box.send_keys(PASSWORD + Keys.ENTER)
    time.sleep(SLEEP_INTERVAL)

    # Let the dashboard load, then navigate to download-history
    load_page()
    driver.get("https://app.bpmsupreme.com/account/download-history")

    # Let the page load before exiting function
    load_page()
          
  def download_library():
    download_button_set = set()
    already_downloaded = set()
    download_count = 0
    while True:
      download_button_set.update(driver.find_elements_by_class_name("hide-mobile"))
      queue = (len(download_button_set) - len(already_downloaded))
      print("Current queue size is: " + str(queue))
      
      # Click every link in the download_button_set
      for button in download_button_set:
        if button in already_downloaded:
          continue
        
        try:
          button.click()
          popup = driver.find_elements_by_class_name("popup")
          download_count += 1

        except:
          print("Could not click button!")
          if download_count != 0:
            download_count -= 1

        # If a popup has appeared, resolve the popup
        if len(popup) != 0:
          download_count -= 1
          print("Detected max download popup! Attempting to resolve...")
          time.sleep(SLEEP_INTERVAL)
          # Click close button on popup
          for attempt in range(0,3):
            try:
              driver.find_element_by_class_name("close").click()
              break
              
            except:
              print("Could not resolve! (Attempt: " + str(attempt + 1) + " of 3)")

      # Scroll down to the bottom of the page
      print("Scrolling to bottom of page")
      
      # Get scroll height.
      last_height = driver.execute_script("return document.body.scrollHeight")

      # Scroll down
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      # Wait to load the page.
      time.sleep(SLEEP_INTERVAL * 10)

      # Calculate new scroll height and compare with last scroll height.
      new_height = driver.execute_script("return document.body.scrollHeight")

      # If the page has loaded, new_height should be bigger
      if new_height <= last_height:
        input("Could not load new song rows! Load new height before pressing ENTER...")

      # Add current button list to already_downloaded set
      print("Downloads completed: " + str(download_count))
      already_downloaded.update(download_button_set)
        
  # MAIN FUNCTION HERE
  # Log into account
  site_login(USERNAME, PASSWORD)
  
  input("Press ENTER to begin downloading files...")
  download_library()
  


