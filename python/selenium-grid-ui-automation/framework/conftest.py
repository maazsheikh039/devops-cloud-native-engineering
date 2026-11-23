import os
import pathlib
import re
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

ARTIFACTS = pathlib.Path(os.getenv("ARTIFACTS_DIR", "artifacts"))


def pytest_addoption(parser):
  parser.addoption(
      "--browser",
      default=os.getenv("BROWSER", "chrome"),
      choices=["chrome", "firefox"],
  )
  parser.addoption(
      "--grid-url", default=os.getenv("GRID_URL", "http://localhost:4444")
  )
  parser.addoption(
      "--app-url", default=os.getenv("APP_URL", "http://webapp:5000")
  )


def _options(browser):
  if browser == "chrome":
    opts = ChromeOptions()
    opts.add_argument("--window-size=1280,900")
  else:
    opts = FirefoxOptions()
    opts.add_argument("--width=1280")
    opts.add_argument("--height=900")
  return opts


@pytest.fixture(scope="session")
def browser_name(request):
  return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def base_url(request):
  return request.config.getoption("--app-url").rstrip("/")


@pytest.fixture
def driver(request, browser_name):
  drv = webdriver.Remote(
      command_executor=request.config.getoption("--grid-url"),
      options=_options(browser_name),
  )
  drv.implicitly_wait(0)
  yield drv
  drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
  """On a failure in the test body, save screenshot + DOM and attach the PNG to pytest-html."""
  outcome = yield
  report = outcome.get_result()
  if report.when != "call" or not report.failed:
    return
  drv = item.funcargs.get("driver")
  if drv is None:
    return
  ARTIFACTS.mkdir(parents=True, exist_ok=True)
  browser = item.config.getoption("--browser")
  safe = re.sub(r"[^A-Za-z0-9_.-]", "_", item.name)
  png = ARTIFACTS / f"FAILED_{browser}_{safe}.png"
  drv.save_screenshot(str(png))
  (ARTIFACTS / f"FAILED_{browser}_{safe}.html").write_text(
      drv.page_source, encoding="utf-8"
  )
  try:
    import pytest_html

    extras = getattr(report, "extras", [])
    extras.append(
        pytest_html.extras.png(
            drv.get_screenshot_as_base64(), "failure screenshot"
        )
    )
    extras.append(pytest_html.extras.url(drv.current_url, "page URL"))
    report.extras = extras
  except ImportError:
    pass
