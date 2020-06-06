# Selenium imports
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import JavascriptException
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
  
  def __init__(self, driver, username, password, download_path, duplicate_path):
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

    # Check paths
    if not isinstance(download_path, str):
      raise TypeError("Wrong type: Expected str for download_path; Got {}".format(type(download_path)))
      
    if not isinstance(duplicate_path, str):
      raise TypeError("Wrong type: Expected str for duplicate_path; Got {}".format(type(duplicate_path)))

    # Check path is valid
    if not os.path.isdir(download_path) or not os.path.isdir(duplicate_path):
      raise ValueError("Bad path: Expected valid path")
    
    self.driver = driver
    self._username = username
    self._password = password
    self.path = download_path
    self.local_library = self.update_library()
    self.path = duplicate_path
    self.local_library.update(self.update_library())

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
    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "table-media")))
    
    # Initialize the current song to first row-container of div.table-media
    current_song = Song(self.driver, self.driver.execute_script(
    """
      return document.getElementsByClassName('table-media')[0].firstChild.firstChild;
    """), self.driver.find_element_by_class_name(
    """
      return document.getElementsByClassName('table-media')[0].firstChild.firstChild;
    """).find_element_by_class_name("hide-mobile"))
    
    # Define tracker for songs that failed the Song.download_song() method
    failed_downloads = set()
    try:
      while current_song.get_next_song():    
        # If current song is a duplicate, track it
        if self.check_duplicate(current_song):
          print("Skipped duplicate: {} - {}".format(current_song.artist, current_song.name))
          failed_downloads.add(current_song)
          current_song = current_song.get_next_song()
          continue
        print("Downloading {} - {}".format(current_song.artist, current_song.name))
        if current_song.download_song() == False:
          print("Could not download {} - {}".format(current_song.artist, current_song.name))

        while self.scroll_page() != True:
          pass

        current_song = current_song.get_next_song()
    except JavascriptException:
      for song in failed_downloads:
        print("Failed to download: {} - {}".format(song.artist, song.name))
      print("{} songs were skipped".format(len(failed_downloads)))
      if len(self.local_library) < len(failed_downloads):
        print("Did not download all songs!")

  def download_new_releases(self, page_count):
    # Get the new-releases page
    self.driver.get("https://app.bpmsupreme.com/new-releases/audio/hip-hop-r%26b")

    # Wait until a .row-container is ready to be clickable
    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "row-container")))

    # Per amount of pages to download
    for page in range(page_count):
      WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "row-container")))

      # Initialize current_song to first row-item container on the page
      current_song = self.driver.execute_script(
      """
        return document.getElementsByClassName('table-media')[0].firstChild.firstChild.firstChild
      """)
      
      # While there is a next row-item
      while current_song:
        # Initialize booleans for duplicate detection on "Quick Hit Dirty" and "Intro Dirty" song versions
        quick_hit_dirty_is_duplicate = False
        intro_dirty_is_duplicate = False
        intro_dirty_is_present = True
        quick_hit_dirty_is_present = True
      
        # Find the "Intro Dirty" and "Quick Hit Dirty" download buttons
        song_versions = self.driver.execute_script(
        """
          return arguments[0].getElementsByClassName('tag-link')
        """, current_song
        )

        # Attempt to find "intro dirty" download button
        try:
          intro_dirty = Song(self.driver, current_song, self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Intro Dirty')
                return arguments[0][i];
            }
            return null;
          """, song_versions))

        except JavascriptException:
          print("Failed finding 'Intro Dirty' download button for {} - {}".format(intro_dirty.artist, intro_dirty.name))
          intro_dirty_is_present = False
        
        except TypeError:
          print("Failed finding 'Intro Dirty' button for {} - {}".format(intro_dirty.artist, intro_dirty.name))
          intro_dirty_is_present = False

        # Attempt to find "quick hit dirty" download button
        try:
          quick_hit_dirty = Song(self.driver, current_song, self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Quick Hit Dirty')
                return arguments[0][i];
            }
            return null;
          """, song_versions))
        
        except JavascriptException:
          print("Failed finding download 'Quick Hit Dirty' button for {} - {}".format(quick_hit_dirty.artist, quick_hit_dirty.name))
          quick_hit_dirty_is_present = False

        except TypeError:
          print("Failed finding download 'Quick Hit Dirty' button for {} - {}".format(intro_dirty.artist, intro_dirty.name))
          quick_hit_dirty_is_present = False

        # Only check for duplicates if there is an existing download button for it
        if intro_dirty_is_present:
          # Check for duplicates
          intro_dirty.name += " (Intro Dirty)"
          intro_dirty_is_duplicate = self.check_duplicate(intro_dirty)
        
        if quick_hit_dirty_is_present:
          quick_hit_dirty.name += " (Quick Hit Dirty)"
          quick_hit_dirty_is_duplicate = self.check_duplicate(quick_hit_dirty)

        # Download songs if not duplicate
        if not intro_dirty_is_duplicate and intro_dirty_is_present:
          print("Downloading: {} - {}".format(intro_dirty.artist, intro_dirty.name))
          intro_dirty.download_song()
          
        if not quick_hit_dirty_is_duplicate and quick_hit_dirty_is_present:
          print("Downloading: {} - {}".format(quick_hit_dirty.artist, quick_hit_dirty.name))          
          quick_hit_dirty.download_song()
        
        # Set current_song to next song
        try:
          current_song = self.driver.execute_script(
          """
          arguments[0].parentNode.parentNode.nextSibling.getElementsByClassName('row-item')[0] ? return arguments[0].parentNode.parentNode.nextSibling.getElementsByClassName('row-item')[0] : return false
          """, current_song)
        except JavascriptException:
          print("Reached end of page: {}".format(page + 1))
          current_song = None
        
      # Find and click the next page button
      try:
        WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "pagination")))
        pagination = self.driver.find_element_by_class_name("pagination").find_elements_by_tag_name("li")
        next_page = self.driver.execute_script(
        """
          for (var i = 0; i < arguments[0].length; ++i) {
            if (arguments[0][i].innerText === '›') {
              return arguments[0][i].firstChild
            }
          }
          return null
        """, pagination)
        next_page.click()
      except JavascriptException(stacktrace=True):
        print("Unable to reach next page")
        break

  def download_exclusives(self, page_count):
    """
    Download exclusives page from BpmSupreme New Releases > Exclusives
  
    Args:
      - page_count: Number of pages from 1 to page_count
    
    Returns:
      - none
  
    Order of song priority:
    Dirty short and dirty extended
    If none, get dirty
    If no dirty, get clean
    If no clean, get clean extended and clean short edit
    """
    # Get the exclusives page
    self.driver.get("https://app.bpmsupreme.com/new-releases/audio/exclusives")

    # Wait until a .row container is ready to be clickable
    WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "row-container")))

    # Per amount of pages to download
    for page in range(page_count):
      WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "row-container")))

      # Initialize current_song to first row-item container on the page
      current_song = self.driver.execute_script(
      """
        return document.getElementsByClassName('table-media')[0].firstChild.firstChild.firstChild.getElementsByClassName('row-item')[0]
      """)  

      # While there is a next row-item
      while current_song:
        # Find all song versions 
        song_versions = self.driver.execute_script(
          """
            return arguments[0].getElementsByClassName('tag-link')
          """, current_song
        )

        # Attempt to find "Dirty Short Edit" and "Dirty Extended" download buttons
        dirty_short = self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Dirty Short Edit')
                return arguments[0][i];
            }
            return null;
          """
        , song_versions)

        # If there is a dirty short version, construct a Song()
        if dirty_short:
          dirty_short = Song(self.driver, current_song, dirty_short)
          dirty_short.name += " (Dirty Short Edit)"

          if self.check_duplicate(dirty_short):
            print("Duplicate: {} - {}".format(dirty_short.artist, dirty_short.name))
          else:
            # Download the song 
            print("Downloaded {} - {}: {}".format(dirty_short.artist, dirty_short.name, dirty_short.download_song()))
            
                  
        dirty_extended = self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Dirty Extended')
                return arguments[0][i];
            }
            return null;
          """
        , song_versions)

        # If there is a dirty extended version, construct a Song()
        if dirty_extended:
          # Convert dirty extended to a Song() object
          dirty_extended = Song(self.driver, current_song, dirty_extended)
          dirty_extended.name += " (Dirty Extended)"
          if self.check_duplicate(dirty_extended):
            print("Duplicate: {} - {}".format(dirty_extended.artist, dirty_extended.name))
          else:
            # Download the song 
            print("Downloaded {} - {}: {}".format(dirty_extended.artist, dirty_extended.name, dirty_extended.download_song()))
            

        # If either versions have been downloaded
        if dirty_short or dirty_extended:
          # Set current_song to next song
          try:
            current_song = self.driver.execute_script(
            """
            return arguments[0].parentNode.parentNode.parentNode.nextSibling.getElementsByClassName('row-item')[0]
            """, current_song)
            continue
          except JavascriptException:
            print("Reached end of page: {}".format(page + 1))
            break

        # Could not find 'dirty short' or 'dirty extended' so look for 'dirty'
        dirty = self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Dirty')
                return arguments[0][i];
            }
            return null;
          """
        , song_versions)

        # If there is a 'dirty' version, construct a Song()
        if dirty:
          dirty = Song(self.driver, current_song, dirty)
          dirty.name += " (Dirty)"

          if self.check_duplicate(dirty):
            print("Duplicate: {} - {}".format(dirty.artist, dirty.name))
          else:
            # Download the song 
            print("Downloaded {} - {}: {}".format(dirty.artist, dirty.name, dirty.download_song()))
            

        # If there is a dirty version, skip to next song
        if dirty:
          # Set current_song to next song
          try:
            current_song = self.driver.execute_script(
            """
            return arguments[0].parentNode.parentNode.parentNode.nextSibling.getElementsByClassName('row-item')[0]
            """, current_song)
            continue
          except JavascriptException:
            print("Reached end of page: {}".format(page + 1))
            break

        # No 'dirty' version, so get 'clean' version
        clean = self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Clean')
                return arguments[0][i];
            }
            return null;
          """
        , song_versions)

        # If there is a 'clean' version, construct a Song()
        if clean:
          clean = Song(self.driver, current_song, clean)
          clean.name += " (Clean)"

          if self.check_duplicate(clean):
            print("Duplicate: {} - {}".format(clean.artist, clean.name))
          else:
            # Download the song 
            print("Downloaded {} - {}: {}".format(clean.artist, clean.name, clean.download_song()))
            

        # If there is a clean version, skip to next song
        if clean:
          # Set current_song to next song
          try:
            current_song = self.driver.execute_script(
            """
            return arguments[0].parentNode.parentNode.parentNode.nextSibling.getElementsByClassName('row-item')[0]
            """, current_song)
            continue
          except JavascriptException:
            print("Reached end of page: {}".format(page + 1))
            break

        # If there is no 'clean' version, get 'clean extended' and 'clean short' edit
        clean_extended = self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Clean Extended')
                return arguments[0][i];
            }
            return null;
          """
        , song_versions)

        # If there is a 'clean extended' version, construct a Song()
        if clean_extended:
          clean_extended = Song(self.driver, current_song, clean_extended)
          clean_extended.name += " (Clean Extended)"

          if self.check_duplicate(clean_extended):
            print("Duplicate: {} - {}".format(clean_extended.artist, clean_extended.name))
          else:
            # Download the song 
            print("Downloaded {} - {}: {}".format(clean_extended.artist, clean_extended.name, clean_extended.download_song()))
            

        clean_short = self.driver.execute_script(
          """
            for(var i = 0; i < arguments[0].length; ++i) {
              if (arguments[0][i].innerText == 'Clean Short Edit')
                return arguments[0][i];
            }
            return null;
          """
        , song_versions)

        # If there is a 'Clean Short Edit' version, construct a Song()
        if clean_short:
          clean_short = Song(self.driver, current_song, clean_short)
          clean_short.name += " (Clean Short Edit)"

          if self.check_duplicate(clean_short):
            print("Duplicate: {} - {}".format(clean_short.artist, clean_short.name))
          else:
            # Download the song 
            print("Downloaded {} - {}: {}".format(clean_short.artist, clean_short.name, clean_short.download_song()))
            

        # If there is a 'Clean Short Edit' version or 'Clean Extended', skip to next song
        if clean_extended or clean_short:
          # Set current_song to next song
          try:
            current_song = self.driver.execute_script(
            """
            return arguments[0].parentNode.parentNode.parentNode.nextSibling.getElementsByClassName('row-item')[0]
            """, current_song)
            continue
          except JavascriptException:
            print("Reached end of page: {}".format(page + 1))
            break
        
        # Move to the next song 
        try:
          current_song = self.driver.execute_script(
          """
          return arguments[0].parentNode.parentNode.parentNode.nextSibling.getElementsByClassName('row-item')[0]
          """, current_song)
        except JavascriptException:
          print("Reached end of page: {}".format(page + 1))
          break

      # Find and click the next page button after all songs have been parsed on page
      try:
        WebDriverWait(self.driver, BpmSupreme.TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "pagination")))
        pagination = self.driver.find_element_by_class_name("pagination").find_elements_by_tag_name("li")
        next_page = self.driver.execute_script(
        """
          for (var i = 0; i < arguments[0].length; ++i) {
            if (arguments[0][i].innerText === '›') {
              return arguments[0][i].firstChild
            }
          }
          return null
        """, pagination)
        next_page.click()
      except JavascriptException(stacktrace=True):
        print("Unable to reach next page")
        break

  def genre_downloads(self):
    """
      Order of Priority
      1. Intro Dirty and Quick Hit Dirty
      2. Intro Clean and Intro Dirty
      3. Dirty and Clean
      4. Clean Short Edit
    """
    pass
  
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
    
    if new_height <= last_height + 60:      
      # Get scroll height.
      last_height = self.driver.execute_script("return document.body.scrollHeight")

      # Scroll down
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

      time.sleep(1)

      # Calculate new scroll height and compare with last scroll height.
      new_height = self.driver.execute_script("return document.body.scrollHeight")
    
    if new_height <= last_height + 60:
      return False
    
    return True


  def update_library(self):
    """
    Initialize a library of current songs using path.
    Returns a set containing all song names within path

    Args:
      - None

    Returns:
      - set containing all song names detected within path
    """
    # Check that path is valid
    if os.path.isdir(self.path) == False:
      raise ValueError("Error: Invalid path provided")
    
    library = set()
    with os.scandir(self.path) as entries:
      for entry in entries:
        file_song_title = entry.name.split(sep=".mp3")[0].split(sep=" - ")[-1].strip()
        library.add(file_song_title)

    return library

  def check_duplicate(self, song):
    """
    Check if duplicate file detected within self.local_library

    Args:
      - song: song to check for in path
    
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
  
  def __init__(self, driver, container, download_button):
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
    if isinstance(container, expected_conditions.WebElement) != True: raise TypeError("Wrong type: {} for container whereas a set is expected".format(type(container)))

    # Check download_button_type
    if isinstance(download_button, expected_conditions.WebElement) != True:
      raise TypeError("Wrong type: Expected WebElement for download_button; Got {}".format(type(download_button)))

    self.driver = driver
    self._container = container
    self.download_button = download_button

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
    
    Returns:
      - True if successful, else False
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

  def get_next_song(self):
    """
    Returns the next sibling of current song using current_song container WebElement

    Args:
      - none 

    Returns:
      Next row-item container based on the current_song
    """
    return self.driver.execute_script(
      """
        if (arguments[0].parentNode.nextSibling.children[0]) {
          return arguments[0].parentNode.nextSibling.children[0];
        }
        return false;
      """)