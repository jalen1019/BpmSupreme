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
    - scroll_page()
  """

  SLEEP_INTERVAL = int()
  
  def __init__(self, driver, username, password):
    """
    Constructor for BpmSupreme object

    Args:
      - driver: WebDriver object
      - username: Username string
      - password: Password string
    """
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
    Logs into https://www.bpmsupreme.com using the defined user credentials
    
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
    Downloads account-history library
    
    Args:
      - none
    """
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