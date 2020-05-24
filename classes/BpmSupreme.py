# Selenium imports
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys

# Standard imports
import time
import getpass

class BpmSupreme:  
  """
  Class representing a BPMSupreme
  
  Methods:
    - site_login()
    - download_library()
  """

  SLEEP_INTERVAL = int()
  
  def __init__(self, driver, username, password):
    self.driver = driver
    self._username = username
    self._password = password
  
  def _load_page(self):
    """
    Utility function to wait for webpages to load
    Args:
      - none
    """
    try:
      WebDriverWait(self.driver, 10).until(expected_conditions.invisibility_of_element_located(self.driver.find_element_by_xpath("//div[@class='loader']")))

    except NoSuchElementException:
      print("Exception Occurred! Waiting " + str(BpmSupreme.SLEEP_INTERVAL) + " seconds before resuming...")
      time.sleep(BpmSupreme.SLEEP_INTERVAL)

  def site_login(self):
    """
    Logs into the site using the defined user credentials
    Args:
      - none
    """
    # Get the initial site page
    self.driver.get("https://www.bpmsupreme.com/")

    # Click on login box at top of page
    self._load_page()
    login_box = self.driver.find_element_by_class_name("user-login-logout")
    login_box.click()

    # Initialize username and password field variables
    self._load_page()
    user_name_box = self.driver.find_element_by_id("login-form-email")
    pass_box = self.driver.find_element_by_id("login-form-password")

    # Input user credentials
    user_name_box.send_keys(self._username + Keys.TAB)
    pass_box.send_keys(self._password + Keys.ENTER)
    time.sleep(BpmSupreme.SLEEP_INTERVAL)

    # Let the dashboard load, then navigate to download-history
    self._load_page()
    self.driver.get("https://app.bpmsupreme.com/account/download-history")

    # Let the page load before exiting function
    self._load_page()
          
  def download_library(self):
    """
    Downloads library account
    Args:
      - none
    """
    download_button_set = set()
    already_downloaded = set()
    while True:
      download_button_set.update(self.driver.find_elements_by_class_name("hide-mobile"))
      queue = (len(download_button_set) - len(already_downloaded))
      print("Current queue size is: " + str(queue))
      
      # Click every link in the download_button_set
      for button in download_button_set:
        if button in already_downloaded:
          continue
        
        try:
          button.click()
          popup = self.driver.find_elements_by_class_name("popup")

        except:
          print("Could not click button!")

        # If a popup has appeared, resolve the popup
        if len(popup) != 0:
          print("Detected max download popup! Attempting to resolve...")
          time.sleep(BpmSupreme.SLEEP_INTERVAL)
          
          # Click close button on popup
          for attempt in range(0,3):
            # If there is no popup present on the page, exit the loop
            if self.driver.find_elements_by_class_name("popup") == 0:
              print("Popup no longer detected on page. Popup resolved...")
              break

            try:
              self.driver.find_element_by_class_name("close").click()
              break
              
            except:
              print("Could not resolve! (Attempt: " + str(attempt + 1) + " of 3")

      # Scroll down to the bottom of the page
      print("Scrolling to bottom of page")
      
      # Get scroll height.
      last_height = self.driver.execute_script("return document.body.scrollHeight")

      # Scroll down
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      # Wait to load the page.
      time.sleep(BpmSupreme.SLEEP_INTERVAL * 10)

      # Calculate new scroll height and compare with last scroll height.
      new_height = self.driver.execute_script("return document.body.scrollHeight")

      # If the page has loaded, new_height should be bigger
      if new_height <= last_height:
        input("Could not load new song rows! Load new height before pressing ENTER...")

      # Add current button list to already_downloaded set
      already_downloaded.update(download_button_set)