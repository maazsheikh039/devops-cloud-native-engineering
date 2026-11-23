"""Task 5: synchronisation, dropdowns and JavaScript alerts."""
import os
import time
import uuid
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

GRID_URL = os.getenv("GRID_URL", "http://localhost:4444")
APP_URL = os.getenv("APP_URL", "http://webapp:5000")
STATS_TIMEOUT = float(os.getenv("STATS_TIMEOUT", "10"))


def login(driver, wait):
  driver.get(f"{APP_URL}/login")
  driver.find_element(By.ID, "username").send_keys("admin")
  driver.find_element(By.ID, "password").send_keys("s3cret")
  driver.find_element(By.ID, "login-btn").click()
  wait.until(EC.url_contains("/tasks"))


def main():
  driver = webdriver.Remote(command_executor=GRID_URL, options=Options())
  driver.implicitly_wait(0)  # explicit waits only - never mix implicit and explicit waits
  wait = WebDriverWait(driver, timeout=10, poll_frequency=0.25)
  try:
    login(driver, wait)

    # 1. Dropdown handling with Select, then wait for the new row after the page reload
    title = f"Upgrade kernel {uuid.uuid4().hex[:6]}"
    driver.find_element(By.ID, "task-title").send_keys(title)
    dropdown = Select(driver.find_element(By.ID, "priority"))
    dropdown.select_by_visible_text("High")
    chosen = dropdown.first_selected_option.get_attribute("value")
    driver.find_element(By.ID, "add-task").click()
    row = wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            f"//tr[td[@class='task-title' and normalize-space()='{title}']]",
        ))
    )
    prio = row.find_element(By.CSS_SELECTOR, "td.task-priority").text
    print(f"[1] added task '{title}' with priority {prio} (dropdown value: {chosen})")

    # 2. The naive approach: look for the result immediately
    driver.find_element(By.ID, "load-stats").click()
    try:
      driver.find_element(By.ID, "stats-total")
      print("[2] naive lookup succeeded (unexpected)")
    except NoSuchElementException as exc:
      status = driver.find_element(By.ID, "stats").text
      print(f"[2] naive lookup failed: {type(exc).__name__}; #stats says '{status}'")

    # 3. The correct approach: an explicit wait for a specific condition
    start = time.monotonic()
    WebDriverWait(driver, STATS_TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "stats-total"))
    )
    waited = time.monotonic() - start
    print(f"[3] stats after explicit wait ({waited:.1f}s): {driver.find_element(By.ID, 'stats').text}")

    # 4. JavaScript confirm(): read the text, then dismiss (Cancel)
    driver.find_element(By.ID, "clear-all").click()
    alert = wait.until(EC.alert_is_present())
    text = alert.text
    alert.dismiss()
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.task-row")
    print(f"[4] alert text: '{text}' -> dismissed, rows: {len(rows)}")

    # 5. JavaScript confirm(): accept (OK) and wait for the page to show the empty state
    driver.find_element(By.ID, "clear-all").click()
    wait.until(EC.alert_is_present()).accept()
    empty = wait.until(EC.visibility_of_element_located((By.ID, "empty-row")))
    print(f"[5] alert accepted, empty row text: {empty.text}")
  finally:
    driver.quit()


if __name__ == "__main__":
  main()
