from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

def scroll_down_github(driver):
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
      # Scroll down to the bottom.
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

      # Wait to load the page.
      time.sleep(6)

      # Calculate new scroll height and compare with last scroll height.
      new_height = driver.execute_script("return document.body.scrollHeight")

      if new_height == last_height:
        break

      last_height = new_height

def test_method(driver):
    library = set()
    while True:
      library.update(driver.find_elements_by_class_name("hide-mobile"))
      print("Current library size is: " + str(len(library)))
      input("Scroll down and then press ENTER...")