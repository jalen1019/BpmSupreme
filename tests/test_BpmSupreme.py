"""
This test file determines if duplicate file detection is working as intended
"""

import pytest
from src.bpm_supreme.classes.BpmSupreme import BpmSupreme
from src.bpm_supreme.classes.BpmSupreme import Song
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions

# Test driver type
def test___init__():
  driver = "Failure"
  with pytest.raises(expected_conditions.WebDriverException):
    obj = BpmSupreme(driver, "Username", "Password")

#