from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from .tasks_page import TasksPage


class LoginPage(BasePage):
  path = "/login"
  USERNAME = (By.ID, "username")
  PASSWORD = (By.NAME, "password")
  SUBMIT = (By.CSS_SELECTOR, "#login-form button[type='submit']")
  ERROR = (By.CSS_SELECTOR, "div.error")

  def _submit(self, user, password):
    self.type(self.USERNAME, user)
    self.type(self.PASSWORD, password)
    self.click(self.SUBMIT)

  def login_as(self, user, password):
    self._submit(user, password)
    self.wait.until(EC.url_contains("/tasks"))
    return TasksPage(self.driver, self.base_url)

  def login_expecting_error(self, user, password):
    self._submit(user, password)
    return self

  def error_text(self):
    return self.find(self.ERROR).text
