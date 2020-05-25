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
  Class representing a BPMSupreme account
  
  Methods:
    - site_login()
    - download_library()
    - scroll_page()
  """

  SLEEP_INTERVAL = 1.25
  
  def __init__(self, driver, username, password):
    """
    Constructor for BpmSupreme object

    Args:
      - driver: WebDriver object
      - username: Username string
      - password: Password string
    """
    # Check argument types
    if isinstance(driver, Firefox) != True: raise expected_conditions.WebDriverException
    if isinstance(username, str) != True: raise TypeError("Bad username arg type")
    if isinstance(password, str) != True: raise TypeError("Bad password arg type")
    
    self.driver = driver
    self._username = username
    self._password = password
  
  def _load_page(self, sleep_time=SLEEP_INTERVAL):
    """
    Utility function to wait for webpages to load

    Args:
      - sleep_time - Wait time if unable to detect loader class
    """
    # Spinning circle element
    loader = self.driver.find_elements_by_xpath("//div[@class='loader']")
    
    # If detect loading element, wait until invisible
    if len(loader) >= 1:
      print("Loading " + self.driver.current_url)
      for element in loader:
        WebDriverWait(self.driver, sleep_time).until(expected_conditions.invisibility_of_element(element))
      time.sleep(sleep_time)
      return True

    time.sleep(sleep_time)
    return False

  def site_login(self):
    """
    Logs into https://www.bpmsupreme.com using the defined user credentials
    
    Args:
      - none
    
    Returns:
      - True if successful login
      - False if failed login
    """
    # Get the login page and let the page load for five seconds
    self.driver.get("https://www.bpmsupreme.com/login")
    self._load_page()

    # Initialize username and password field variables
    user_name_box = self.driver.find_element_by_id("login-form-email")
    pass_box = self.driver.find_element_by_id("login-form-password")

    # Input user credentials
    user_name_box.click()
    user_name_box.send_keys(self._username + Keys.TAB)
    pass_box.send_keys(self._password + Keys.ENTER)
    self._load_page()

    # Check if site log in was successful
    if self.driver.current_url == "https://www.bpmsupreme.com/login":
      # Site login failed
      return False
    
    # Let login page load before exiting
    self._load_page()
    return True
          
  def download_library(self):
    """
    Downloads account-history library
    
    Args:
      - none
    """

    # Navigate to download-history
    self.driver.get("https://app.bpmsupreme.com/account/download-history")

    # Let the page load before exiting function
    self._load_page()
    
    already_downloaded = set()
    rows_on_page = set()
    songs_to_download = set()
    while True:
      # Add all current songs to a set
      rows_on_page = self.driver.find_elements_by_class_name("row-item")
      for row in rows_on_page:
        songs_to_download.add(Song(self.driver, row))
      
      for song in songs_to_download:
        if song in already_downloaded:
          continue
        song.download_song()
        already_downloaded.add(song)
        print("Downloaded " + song.name + " by " + song.artist)

      # Scroll down to the bottom of the page
      print("Scrolling to bottom of page")
      self.scroll_page()
  
  def scroll_page(self):
    """
    Scrolls the page down.

    Args:
      - none
    """
    last_height = 1
    new_height = 0
    
    while new_height <= last_height:
      # Get scroll height.
      last_height = self.driver.execute_script("return document.body.scrollHeight")

      # Scroll down
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      # Wait to load the page.
      time.sleep(BpmSupreme.SLEEP_INTERVAL * 10)

      # Calculate new scroll height and compare with last scroll height.
      new_height = self.driver.execute_script("return document.body.scrollHeight")


class Song():
  """
  Object representing a BPMSupreme song

  Methods:
    - download_song()

  Properties:
    - name: Song name
    - artist: Song artist
  """
  def __init__(self, driver, container):
    """
    Song constructor
    Args:
      - driver: Selenium WebDriver object
      - container: row-item WebElement
    """
    
    # Check argument types
    if driver is not Firefox: raise expected_conditions.WebDriverException
    if container is not expected_conditions.WebElement: raise TypeError

    self.driver = driver
    self._container = container

    # Find child elements of row-item container matching song details
    self.name = self._container.find_element_by_class_name("row-track-name").find_element_by_name("span").text
    self.artist = self._container.find_element_by_class_name("row-artist").find_element_by_class_name("link").text

    # Find download button of row-item
    self.download_button = self._container.find_element_by_class_name("hide-mobile")

  def __hash__(self):
    return hash((self._container))

  def __eq__(self, other):
    if not isinstance(other, type(self)): return NotImplemented
    return self._container == other._container

  def download_song(self):
    """
    Clicks the download_song button

    Args:
      - none
    """
    try:
      self.download_button.click()
      # Find any class associated with a popup
      popup = self.driver.find_elements_by_class_name("popup")

    except:
      print("Could not click download button!")

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
          # Try to click the close button
          self.driver.find_element_by_class_name("close").click()
          break
        
        # Loop back around if unable to resolve on current attempt
        except:
          print("Could not resolve! (Attempt: " + str(attempt + 1) + " of 3")

  @property
  def name(self):
    """The name of the song"""
    return self.name
  
  @property
  def artist(self):
    """The artist of the song"""
    return self.artist

  @property
  def download_button(self):
    """WebElement of download button of song"""
    return self.download_button