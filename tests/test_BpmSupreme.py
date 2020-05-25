"""
This test file determines if BpmSupreme class methods are working correctly
"""

import pytest
from selenium.common import exceptions as selenium_exceptions
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
  def test_login(self, account):
    # Check login()
    assert account.login() == True
    
    # Navigate to the download-history
    account.driver.get("https://app.bpmsupreme.com/account/download-history")

    # Check scroll_page()
    assert account.scroll_page() == True

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

    
