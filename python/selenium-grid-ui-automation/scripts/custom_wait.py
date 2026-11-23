"""Task 5 extension: a custom wait condition."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

d = webdriver.Remote(command_executor="http://localhost:4444", options=Options())
try:
  d.get("http://webapp:5000/login")
  d.find_element(By.ID, "username").send_keys("admin")
  d.find_element(By.ID, "password").send_keys("s3cret")
  d.find_element(By.ID, "login-btn").click()
  WebDriverWait(d, 10).until(lambda drv: drv.current_url.endswith("/tasks"))
  d.find_element(By.ID, "load-stats").click()
  condition = lambda drv: drv.find_element(By.ID, "stats").text.startswith("Total tasks:")
  WebDriverWait(d, 10).until(condition)
  print("custom wait ok:", d.find_element(By.ID, "stats").text)
finally:
  d.quit()
