# `taskboard-selenium-grid`: Cross-Browser UI Test Automation on Selenium Grid 4

## Objectives
- Containerise **TaskBoard**, a Flask web application with session-isolated tasks, delayed AJAX statistics (`/api/stats`), and a JavaScript `confirm()` delete workflow.
- Deploy **Selenium Grid 4** (`selenium/hub`, `selenium/node-chrome`, `selenium/node-firefox`) via Docker Compose with `shm_size: "1gb"` and multi-slot node concurrency, inspecting cluster state through `/status`, GraphQL, and raw W3C WebDriver HTTP calls.
- Practise locator strategies (`By.ID`, `By.NAME`, `By.CSS_SELECTOR`, `By.XPATH`, `By.TAG_NAME`), explicit waits (`WebDriverWait` + `expected_conditions` + custom predicates), `Select` dropdowns, and `Alert` handling while avoiding implicit-wait mixing and `time.sleep()`.
- Build a maintainable **Page Object Model** `pytest` framework with custom CLI flags (`--browser`, `--grid-url`, `--app-url`), parametrisation, markers (`@pytest.mark.smoke`), failure screenshot/DOM hooks, `pytest-html` and JUnit XML reporting, and `pytest-xdist` parallel execution.
- Package the test suite into a container image and orchestrate readiness polling, a smoke gate, and a cross-browser regression matrix in `run_ci.sh`.

## Tools Used
- **Test Automation & Reporting:** Python `3.10+`, `selenium` (`4.18.1`), `pytest` (`8.0.2`), `pytest-html` (`4.1.1`), `pytest-xdist` (`3.5.0`)
- **Application & Container Stack:** Flask (`3.0.2`), Werkzeug (`3.0.1`), Gunicorn (`21.2.0`), Docker Engine, Docker Compose, `selenium/hub:4.18.1-20240224`, `selenium/node-chrome:4.18.1-20240224`, `selenium/node-firefox:4.18.1-20240224`
- **CLI & Verification Utilities:** `curl`, `jq`, `file`, `git`

## Key Skills Demonstrated
- **Distributed Browser Grid Operations:** Configuring hub/node event buses, `shm_size`, and session slots, querying Grid GraphQL/status endpoints, and cleaning up leaked sessions.
- **Reliable Web Synchronization:** Using explicit `WebDriverWait` conditions and custom callables for asynchronous UI updates and browser dialogs without race conditions or fixed sleeps.
- **Test Architecture & CI Readiness:** Structuring page objects, fixtures, failure evidence capture, parallel test isolation, and exit-code-driven CI gates.

## Troubleshooting Log
- **Malformed PDF Commands & Syntax:** Fixed broken flags, missing spaces/dashes, LaTeX math artifacts, and typos across lab scripts, page objects, Compose files, `run_ci.sh`, and `validate.sh`.
- **Container Network Addressing (`localhost` vs. `webapp`):** Resolved `net::ERR_CONNECTION_REFUSED` inside browser nodes by targeting `http://webapp:5000` over the shared Docker Compose network instead of `localhost:5000`.
- **Leaked WebDriver Sessions:** Identified unclosed sessions via Grid `/status` and GraphQL `sessionCount` and terminated orphaned sessions via `DELETE /session/<id>`.
- **Premature AJAX Lookups & Undersized Timeouts:** Demonstrated `NoSuchElementException` on immediate lookup before the 2.5 s `/api/stats` fetch completes and `TimeoutException` when `STATS_TIMEOUT=1` is set too low.
- **Artifact File Ownership in CI:** Passed `HOST_UID` and `HOST_GID` into the `tests` service so generated HTML and JUnit reports in `artifacts/ci/` are owned by the host user.
