import os
import uuid
import pytest
from pages.login_page import LoginPage


@pytest.fixture
def tasks_page(driver, base_url):
  return LoginPage(driver, base_url).open().login_as("admin", "s3cret")


def test_default_tasks(tasks_page):
  assert tasks_page.task_titles() == ["Patch web servers", "Rotate log files"]


def test_add_task(tasks_page):
  title = f"Deploy release {uuid.uuid4().hex[:6]}"
  tasks_page.add_task(title, "High")
  assert title in tasks_page.task_titles()


def test_empty_title_rejected(tasks_page):
  assert tasks_page.submit_empty_title() == "Title is required"


def test_stats_after_adding_high_task(tasks_page):
  tasks_page.add_task(f"Renew TLS certs {uuid.uuid4().hex[:6]}", "High")
  assert tasks_page.load_stats() == {"total": 3, "high": 2}


def test_cancel_delete_keeps_tasks(tasks_page):
  assert tasks_page.clear_all(accept=False) == "Delete all tasks?"
  assert len(tasks_page.task_titles()) == 2


def test_delete_all(tasks_page):
  tasks_page.clear_all(accept=True)
  assert tasks_page.task_titles() == []


def test_intentional_failure(tasks_page):
  if os.getenv("FAIL_DEMO") != "1":
    pytest.skip("set FAIL_DEMO=1 to demonstrate failure artifacts")
  assert tasks_page.heading() == "My Projects"
