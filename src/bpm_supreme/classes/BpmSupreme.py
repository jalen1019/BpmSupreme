# Selenium imports
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Standard imports
import time
import getpass
import os

class BpmSupreme:  
  """
  Class representing a BPMSupreme account
  
  Methods:
    - load_page()
    - site_login()
    - download_library()
    - scroll_page()
    - detect_duplicates()
  """

  # Amount of time to wait for a WebElement to load
  TIMEOUT = 120
  SCROLL_PAGE_WAIT_TIME = 5
  
  def __init__(self, driver, username, password, path):
    """
    Constructor for BpmSupreme object

    Args:
      - driver: WebDriver object
      - username: Username string
      - password: Password string
    """
    # Check argument types
    # Check driver
    if isinstance(driver, Firefox) != True: raise expected_conditions.WebDriverException(msg="Wrong type: {} for driver whereas a Firefox WebDriver is expected".format(type(driver)))

    # Check username
    if isinstance(username, str) != True: raise TypeError("Wrong type: {} for username whereas a str is expected".format(type(username)))
    
    # Check password
    if isinstance(password, str) != True: raise TypeError("Wrong type: {} for password whereas a str is expected".format(type(password)))

    # Check path is string
    if isinstance(path, str) != True:
      raise TypeError("Wrong type: Expected str for path; Got {}".format(type(path)))

    # Check path is valid
    if os.path.isdir(path) != True:
      raise ValueError("Bad path: Expected valid path for path")
    
    self.driver = driver
    self._username = username
    self._password = password
    self.path = path
    self.local_library = self.update_library()

  def login(self):
    """
    Logs into https://www.bpmsupreme.com using the defined user credentials
    
    Args:
      - none
    
    Returns:
      - True if successful login
      - False if failed login
    """
    # Get the login page and let the page load
    self.driver.get("https://www.bpmsupreme.com/login")

    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.invisibility_of_element((By.CLASS_NAME, "loader")))

    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.ID, "login-form-email")))
    
    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.ID, "login-form-password")))

    # Input user credentials
    user_name_box = self.driver.find_element(By.ID, "login-form-email")
    user_name_box.click()
    user_name_box.send_keys(self._username)

    # Input password credentials
    pass_box = self.driver.find_element(By.ID, "login-form-password")
    pass_box.click()
    pass_box.send_keys(self._password + Keys.ENTER)

    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".account-menu-toggle")))

    # Check if site log in was successful
    if self.driver.current_url == "https://www.bpmsupreme.com/login":
      # Site login failed
      raise ValueError("Could not log into account using credentials:\nUser: {}\n Password: {}".format(self._username, self._password))

    return True
          
  def download_account_history(self):
    """
    Downloads account-history library
    
    Args:
      - none
    """

    # Navigate to download-history
    self.driver.get("https://app.bpmsupreme.com/account/download-history")

    # Let the page load
    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "download-history")))
    
    songs_on_page = set()
    songs_to_skip = set()
    while True:
      songs_on_page.update(self.get_songs())
    
      for song_on_page in songs_on_page:
        if song_on_page in songs_to_skip:
          continue
        if self.check_duplicate(song_on_page):
          print("Detected duplicate: {} - {}".format(song_on_page.artist, song_on_page.name))
          continue
        print("Downloading {} - {}".format(song_on_page.artist, song_on_page.name))
        if song_on_page.download_song() == False:
          print("Could not download: {} - {}".format(song_on_page.artist, song_on_page.name))
      songs_to_skip.add(song_on_page)
      self.scroll_page()
  
  def scroll_page(self, load_page_time=SCROLL_PAGE_WAIT_TIME):
    """
    Scrolls the page down.

    Args:
      - none

    Returns:
      - True if successful page scroll
      - False if unsuccessful page scroll
    """

    WebDriverWait(self.driver, load_page_time).until(expected_conditions.invisibility_of_element((By.CLASS_NAME, "loader")))
    
    last_height = 60
    new_height = 0
    
    while new_height <= last_height + 60:      
      # Get scroll height.
      last_height = self.driver.execute_script("return document.body.scrollHeight")

      # Scroll down
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

      time.sleep(1)

      # Calculate new scroll height and compare with last scroll height.
      new_height = self.driver.execute_script("return document.body.scrollHeight")

    print("Document height changed from " + str(last_height) + " to " + str(new_height))

    return True

  def get_songs(self):
    """
    Returns all current songs on the page

    Args:
      - None
    
    Returns:
      - Set object containing all current songs on the page
    """
    WebDriverWait(self.driver, 120).until(expected_conditions.visibility_of_all_elements_located((By.CLASS_NAME, "row-item")))
    row_items = self.driver.find_elements_by_class_name("row-item")
    
    # Add all songs on page to set
    library = set()
    for item in row_items:
      library.add(Song(self.driver, item))
    return library

  def update_library(self):
    """
    Initialize a library of current songs using path.
    Returns a set containing all song names within path

    Args:
      - path: string path to directory to check for duplicates

    Returns:
      - set containing all song names detected within path
    """
    # Check that path is valid
    if os.path.isdir(self.path) == False:
      raise ValueError("Error: Invalid path provided")
    
    library = set()
    with os.scandir(self.path) as entries:
      for entry in entries:
        file_song_title = entry.name.split(sep=".mp3")[0].split(sep="-")[-1].strip()
        library.add(file_song_title)

    return library

  def check_duplicate(self, song, path='.'):
    """
    Check if duplicate file detected within path

    Args:
      - song: song to check for in path
      - path: string path to directory to check for duplicates
    
    Returns:
      True if found duplicate, else returns False
    """    

    if isinstance(song, Song) == False:
      raise TypeError("Expected argument of type Song() for arg song, instead got {}".format(type(song)))
    
    for song_name in self.local_library:
      if song.name == song_name:
        # Duplicate song name found in library
        return True

    # No duplicate song found in library
    return False

class Song():
  """
  Object representing a BPMSupreme song

  Methods:
    - download_song()

  Properties:
    - name: Song name
    - artist: Song artist
  """

  SLEEP_INTERVAL = 1.25
  
  def __init__(self, driver, container):
    """
    Song constructor
    Args:
      - driver: Selenium Firefox WebDriver object
      - container: row-item WebElement
    """
    
    # Check argument types
    # Check driver type
    if isinstance(driver, Firefox) != True : raise expected_conditions.WebDriverException(msg="Wrong type: {} for driver whereas a Firefox WebDriver is expected".format(type(driver)))
    
    # Check container type
    if isinstance(container, expected_conditions.WebElement) != True: raise TypeError("Wrong type: {} for container whereas a WebElement is expected".format(type(container)))

    self.driver = driver
    self._container = container

    # Find child elements of row-item container matching song details
    # Try to detect artist name
    try:
      track_name_container = self._container.find_element_by_class_name("row-track-name").find_element_by_css_selector("span")
      self.name = track_name_container.text
    
    except NoSuchElementException:
      print("Unable to detect track name from {}".format(self._container.tag_name))
      self.name = "Unknown"

    # Try to detect song name
    try:
      artists = []
      for element in self._container.find_element_by_class_name("row-artist").find_elements_by_class_name("link"):
        artists.append(element.text)
      self.artist = ", ".join(artists)
    except NoSuchElementException:
      print("Unable to detect artist name from {}".format(self._container.tag_name))
      self.artist = "Unknown"

    # Try to find download button of song
    try:
      self.download_button = self._container.find_element_by_class_name("hide-mobile")
    except NoSuchElementException:
      print("Unable to detect download button for {} - {}".format(self.artist, self.name))
      self.download_button = "Unknown"

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
    result = True
    try:
      self.download_button.click()      

    except:
      print("Could not click download button!")
      result = False

    # Try to detect popup
    try:      
      # Look for popup on screen
      popup = WebDriverWait(self.driver, 2.5).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "popup_inner")))
      
      # Find useful popup elements
      popup_text_title = WebDriverWait(self.driver, 2.5).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "title")))
      close_button = WebDriverWait(self.driver, 2.5).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "div.close")))

      # Double check we're looking at the correct popup
      if popup_text_title.text == "Download Limit":
        result = False
        print("Detected max download popup! Attempting to resolve...")
        # Wait until close_button is clickable
        WebDriverWait(self.driver, 120).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "div.close")))
        close_button.click()

    # No popup has been detected
    except TimeoutException:
      pass

    return result