"""Task 3: open a Remote WebDriver session, inspect capabilities, take a screenshot."""
import os
import pathlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

GRID_URL = os.getenv("GRID_URL", "http://localhost:4444")
APP_URL = os.getenv("APP_URL", "http://webapp:5000")
OUT = pathlib.Path("artifacts")
OUT.mkdir(exist_ok=True)

options = ChromeOptions()
options.add_argument("--window-size=1280,900")
driver = webdriver.Remote(command_executor=GRID_URL, options=options)
try:
  caps = driver.capabilities
  print("session id:", driver.session_id)
  print("browser   :", caps["browserName"], caps["browserVersion"])
  print("platform  :", caps.get("platformName"))
  driver.get(f"{APP_URL}/")
  print("title     :", driver.title)
  print("url       :", driver.current_url)
  driver.save_screenshot(str(OUT / "home.png"))
  print("screenshot:", OUT / "home.png")
finally:
  driver.quit()
