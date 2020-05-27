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
def account(username, password):
  """
  Provides BpmSupreme account object
  """
  driver = Firefox()
  account = BpmSupreme(driver, username, password)
  yield account
  print("Tearing down Selenium Firefox WebDriver")
  driver.quit()

class TestBpmSupreme():
  """
  Class for testing BpmSupreme() methods
  """
  
  # Check BpmSupreme constructor argument validation
  def test_constructor(self):
    with Firefox() as driver:
      # Bad webdriver
      with pytest.raises(selenium_exceptions.WebDriverException):
        BpmSupreme("Driver", "Username", "Password")

      # Bad username
      with pytest.raises(TypeError):
        BpmSupreme(driver, driver, "password")
        driver.close()

      # Bad password
      with pytest.raises(TypeError):
        BpmSupreme(driver, "username", driver)
        driver.close()

  # Check login() and scroll_page()
  def test_login(self, account, username, password):
    # Check login()
    assert account.login(), \
      "Could not log into account using credentials:\nUser: {}\nPassword: {}".format(username, password) 
    
    # Navigate to the download-history
    account.driver.get("https://app.bpmsupreme.com/account/download-history")

    # Check scroll_page()
    assert account.scroll_page()

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
    for song in get_songs():
      if song.name == bad_song_name:
        song_found = True
        assert song.download_song() == False, "Expected download to fail!"

    assert song_found, "The song could not be found on the page"

