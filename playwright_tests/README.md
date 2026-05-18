# Playwright Automated Test Suite
### Login · Employee Setup · Updates · Logoff

A beginner-friendly automated test project using **Python + Playwright + pytest**.

---

## Test sites

| Site | Used for |
|------|----------|
| `the-internet.herokuapp.com` | Login & logoff tests |
| `parabank.parasoft.com` | Employee registration & profile updates |

Both are public, purpose-built sites for test automation practice.

---

## Quick start

### 1. Install Python 3.8+
Download from https://python.org if needed.

### 2. Install dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 3. Run all tests
```bash
pytest
```

### 4. Open the HTML report
After running, open `reports/test_report.html` in your browser.

---

## Project structure

```
playwright_tests/
│
├── conftest.py             # Shared fixtures (browser, logged-in sessions)
├── pytest.ini              # pytest config & default flags
├── requirements.txt        # Python dependencies
│
├── pages/                  # Page Object Model (POM)
│   ├── login_page.py       # Selectors + actions for the login form
│   └── employee_page.py    # Selectors + actions for registration & profile
│
├── tests/
│   ├── test_login.py       # 6 login test cases (valid, invalid, empty)
│   ├── test_employee.py    # 3 registration tests (success, duplicate, missing field)
│   ├── test_update.py      # 4 update tests (phone, table sort, row find)
│   └── test_logoff.py      # 6 logout tests (redirect, flash, session invalidation)
│
└── reports/
    ├── test_report.html    # Generated after running pytest
    └── videos/             # Screen recordings of each test run
```

---

## Running specific tests

```bash
# One file
pytest tests/test_login.py -v

# One specific test
pytest tests/test_login.py::test_valid_login_redirects_to_secure -v

# Watch mode (re-run on file save)
pip install pytest-watch
ptw tests/

# Headed mode (watch the browser)
pytest --headed

# Slow down for visibility
pytest --headed --slowmo=500
```

---

## Useful pytest flags

| Flag | Effect |
|------|--------|
| `-v` | Verbose output |
| `--headed` | Show the browser window |
| `--slowmo=500` | Add 500ms delay between actions |
| `-x` | Stop on first failure |
| `-k "login"` | Run only tests whose name contains "login" |
| `--tb=long` | Full traceback on failures |

---

## Understanding the Page Object Model

Instead of writing selectors directly in tests:
```python
# ❌ Without POM — brittle, hard to maintain
page.fill("#username", "tomsmith")
page.fill("#password", "SuperSecretPassword!")
page.click('button[type="submit"]')
```

We define them once in a Page Object:
```python
# ✅ With POM — clean tests, easy to update
lp = LoginPage(page)
lp.goto()
lp.login("tomsmith", "SuperSecretPassword!")
```

If the selector `#username` ever changes, you fix it in **one file** (`login_page.py`),
not in every test that uses it.

---

## Credentials

| Site | Username | Password |
|------|----------|----------|
| the-internet | `tomsmith` | `SuperSecretPassword!` |
| ParaBank | `john` | `demo` |

---

## Next steps

- Add `pytest-xdist` to run tests in parallel: `pytest -n auto`
- Connect to GitHub Actions for CI/CD (`.github/workflows/tests.yml`)
- Add `allure-pytest` for richer reports
- Expand the POM to cover more ParaBank pages (transfers, bill pay)
