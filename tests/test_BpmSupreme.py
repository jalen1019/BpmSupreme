"""
This test file determines if BpmSupreme class methods are working correctly
"""

import pytest
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox

from src.bpm_supreme.classes.BpmSupreme import BpmSupreme
from src.bpm_supreme.classes.BpmSupreme import Song

@pytest.fixture
def account(username, password, download_dir):
  """
  Provides BpmSupreme account object
  """
  driver = Firefox()
  account = BpmSupreme(driver, username, password, download_dir)
  yield account
  print("Tearing down Selenium Firefox WebDriver")
  driver.quit()

class TestBpmSupreme():
  """
  Class for testing BpmSupreme() methods
  """
  
  # Check BpmSupreme constructor argument validation
  def test_constructor(self, download_dir):
    with Firefox() as driver:
      # Bad webdriver
      with pytest.raises(selenium_exceptions.WebDriverException):
        BpmSupreme("Driver", "Username", "Password", download_dir)

      # Bad username
      with pytest.raises(TypeError):
        BpmSupreme(driver, driver, "password", download_dir)
        driver.close()

      # Bad password
      with pytest.raises(TypeError):
        BpmSupreme(driver, "username", driver, download_dir)
        driver.close()

      # Bad path type
      with pytest.raises(TypeError):
        BpmSupreme(driver, "username", "password", 123)

  # Check login() and scroll_page()
  def test_login(self, account, username, password):
    # Check login()
    assert account.login(), \
      "Could not log into account using credentials:\nUser: {}\nPassword: {}".format(username, password) 
    
    # Navigate to the download-history
    account.driver.get("https://app.bpmsupreme.com/account/download-history")

    # Check scroll_page()
    assert account.scroll_page()

  def test_update_library(self, account, download_dir, duplicate_song):
    library = account.update_library(download_dir)
    for song in library:
      print(song)
      if song == duplicate_song:
        assert song==duplicate_song, "{} not detected in local library".format(duplicate_song)
        return 

  def test_check_duplicate(self, account, duplicate_song, download_dir):
    assert duplicate_song in account.local_library, "{} not detected in local library".format(duplicate_song)
    
    # Log into BpmSupreme account
    account.login()
    # Navigate to download history page
    account.driver.get("https://app.bpmsupreme.com/account/download-history")
    
    # Get all the songs on the site after scrolling 3 times
    songs_on_page = set()
    for page in range(3):
      account.scroll_page()
    songs_on_page = account.get_songs()

    # Search for duplicate song string inside of songs_on_page
    for song in songs_on_page:
      if song.name == duplicate_song:
        print("{} is detected on page.".format(duplicate_song))
        break
    assert account.check_duplicate(song, path=download_dir), "Could not find {} within {}".format(duplicate_song, download_dir)
        


class TestSong():
  """
  Class for testing Song() methods
  """
  def test_constructor(self):
    with Firefox() as driver:
      # Bad driver
      with pytest.raises(selenium_exceptions.WebDriverException):
        Song("Driver", driver.create_web_element("element"))
      
      # Bad container
      with pytest.raises(TypeError):
        Song(driver, "WebElement")
        driver.close()

  def test_download_song(self, account, bad_song_name):
    # Log into account
    assert account.login()

    # Navigate to the download-history
    account.driver.get("https://app.bpmsupreme.com/account/download-history")
    
    library = account.get_songs()
    for song in library:
      print("Detected: {} - {}".format(song.artist, song.name))
    assert account.scroll_page()
    print("Songs detected on page: " + str(len(account.get_songs())))
    assert len(account.get_songs()) > 40
    
    # Attempt to download `bad-song-name` config option
    song_found = False
    for song in account.get_songs():
      if song.name == bad_song_name:
        song_found = True
        assert song.download_song() == False, "Expected download to fail!"

    assert song_found, "The song could not be found on the page"