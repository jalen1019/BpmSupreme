"""
This test file determines if BpmSupreme class methods are working correctly
"""

import pytest
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver import Firefox

from src.bpm_supreme.classes.BpmSupreme import BpmSupreme

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

# Check BpmSupreme constructor argument validation
def test_constructor():
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
def test_login(account):
  # Check login()
  assert account.login() == True
  
  # Navigate to the download-history
  account.driver.get("https://app.bpmsupreme.com/account/download-history")

  # Check scroll_page()
  assert account.scroll_page() == True