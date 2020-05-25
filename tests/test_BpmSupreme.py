"""
This test file determines if BpmSupreme class methods are working correctly
"""

import pytest
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver import Firefox

from src.bpm_supreme.classes.BpmSupreme import BpmSupreme

@pytest.fixture
def account(username, password):
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

# Check site_login()
def test_site_login(account):
  assert account.site_login() == True