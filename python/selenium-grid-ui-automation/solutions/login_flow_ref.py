"""Task 4: locator strategies and basic interactions."""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

GRID_URL = os.getenv("GRID_URL", "http://localhost:4444")
APP_URL = os.getenv("APP_URL", "http://webapp:5000")


def main():
  driver = webdriver.Remote(command_executor=GRID_URL, options=Options())
  driver.implicitly_wait(2)  # acceptable for this simple script; Task 5 explains why we drop it
  try:
    driver.get(f"{APP_URL}/login")
    print(f"[1] title on /login: {driver.title}")

    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("s3cret")
    driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']").click()
    print(f"[2] after login URL: {driver.current_url}")

    heading = driver.find_element(By.TAG_NAME, "h1").text
    print(f"[3] heading: {heading}")

    user = driver.find_element(By.ID, "current-user").text
    print(f"[4] logged in as: {user}")

    rows = driver.find_elements(By.XPATH, "//table[@id='task-table']/tbody/tr[@class='task-row']")
    print(f"[5] task rows: {len(rows)}")

    first_title = rows[0].find_element(By.CSS_SELECTOR, "td.task-title").text
    first_prio = rows[0].find_element(By.CSS_SELECTOR, "td.task-priority").text
    print(f"[6] first task: {first_title} ({first_prio})")

    # Negative path: log out, then try a wrong password
    driver.get(f"{APP_URL}/logout")
    driver.get(f"{APP_URL}/login")
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("wrong-password")
    driver.find_element(By.ID, "login-btn").click()
    error = driver.find_element(By.CSS_SELECTOR, "div.error").text
    print(f"[7] negative login error: {error}")
  finally:
    driver.quit()


if __name__ == "__main__":
  main()
