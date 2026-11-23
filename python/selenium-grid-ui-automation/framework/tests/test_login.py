import pytest
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_home_title(driver, base_url):
  driver.get(base_url + "/")
  assert driver.title == "TaskBoard - Home"


@pytest.mark.smoke
def test_valid_login(driver, base_url):
  tasks = LoginPage(driver, base_url).open().login_as("admin", "s3cret")
  assert tasks.heading() == "My Tasks"
  assert tasks.current_user() == "admin"


@pytest.mark.parametrize(
    "user, password",
    [
        ("admin", "wrong"),
        ("nobody", "s3cret"),
        ("", ""),
    ],
)
def test_invalid_login(driver, base_url, user, password):
  page = LoginPage(driver, base_url).open().login_expecting_error(user, password)
  assert page.error_text() == "Invalid username or password"
  assert driver.current_url.endswith("/login")
