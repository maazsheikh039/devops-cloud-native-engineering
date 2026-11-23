"""Deliberately forgets driver.quit() to simulate a crashed test."""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

driver = webdriver.Remote(
    command_executor=os.getenv("GRID_URL", "http://localhost:4444"),
    options=Options(),
)
driver.get("http://webapp:5000/")
print("leaked session:", driver.session_id)
