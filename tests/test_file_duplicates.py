"""
This test file determines if duplicate file detection is working as intended
"""

import pytest
from src.bpm_supreme.classes.BpmSupreme import BpmSupreme
from src.bpm_supreme.classes.BpmSupreme import Song
from selenium.webdriver import Firefox

class test_bpm_supreme:
  def test___init__(self):
    driver = "test"
    with pytest.raises(TypeError) as exception_info:
      obj = BpmSupreme(driver, "Username", "Password")