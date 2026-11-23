from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from .base_page import BasePage


class TasksPage(BasePage):
  path = "/tasks"
  HEADING = (By.TAG_NAME, "h1")
  CURRENT_USER = (By.ID, "current-user")
  TITLE_INPUT = (By.ID, "task-title")
  PRIORITY = (By.ID, "priority")
  ADD = (By.ID, "add-task")
  ROW_TITLES = (By.CSS_SELECTOR, "#task-table tbody tr.task-row td.task-title")
  EMPTY_ROW = (By.ID, "empty-row")
  LOAD_STATS = (By.ID, "load-stats")
  STATS_TOTAL = (By.ID, "stats-total")
  STATS_HIGH = (By.ID, "stats-high")
  CLEAR_ALL = (By.ID, "clear-all")
  ERROR = (By.CSS_SELECTOR, "div.error")

  def heading(self):
    return self.find(self.HEADING).text

  def current_user(self):
    return self.find(self.CURRENT_USER).text

  def task_titles(self):
    return [e.text for e in self.driver.find_elements(*self.ROW_TITLES)]

  def submit_empty_title(self):
    self.find(self.TITLE_INPUT).clear()
    self.click(self.ADD)
    return self.find(self.ERROR).text

  def add_task(self, title, priority_label="Medium"):
    self.type(self.TITLE_INPUT, title)
    Select(self.find(self.PRIORITY)).select_by_visible_text(priority_label)
    self.click(self.ADD)
    self.find((By.XPATH, f"//td[@class='task-title' and normalize-space()='{title}']"))
    return self

  def load_stats(self):
    self.click(self.LOAD_STATS)
    total = self.find(self.STATS_TOTAL).text
    high = self.find(self.STATS_HIGH).text
    return {"total": int(total), "high": int(high)}

  def clear_all(self, accept=True):
    self.click(self.CLEAR_ALL)
    alert = self.wait.until(EC.alert_is_present())
    text = alert.text
    if accept:
      alert.accept()
      self.find(self.EMPTY_ROW)
    else:
      alert.dismiss()
    return text
