import pytest
from playwright.sync_api import sync_playwright

TIMEOUT = 60000  # 60 seconds — accounts for slow live sites


# ── Browser & page fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_instance():
    """Launch a single browser for the whole test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        yield browser
        browser.close()


@pytest.fixture
def page(browser_instance):
    """Give each test its own fresh browser context (clean cookies/session)."""
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 800},
        record_video_dir="reports/videos/"
    )
    page = context.new_page()
    page.set_default_timeout(TIMEOUT)        # global timeout for all actions
    page.set_default_navigation_timeout(TIMEOUT)
    yield page
    context.close()


# ── Shared login helper ───────────────────────────────────────────────────────

@pytest.fixture
def logged_in_page(page):
    """Return a page that is already logged in to the-internet."""
    page.goto("https://the-internet.herokuapp.com/login",
              wait_until="domcontentloaded")
    page.locator("#username").wait_for(state="visible")
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.click('button[type="submit"]')
    page.wait_for_url("**/secure", timeout=TIMEOUT)
    assert page.url.endswith("/secure"), "Login failed in fixture"
    return page


@pytest.fixture
def parabank_logged_in(page):
    """Return a page that is already logged in to ParaBank (demo account)."""
    page.goto("https://parabank.parasoft.com/parabank/login.htm",
              wait_until="domcontentloaded")
    page.locator('input[name="username"]').wait_for(state="visible")
    page.fill('input[name="username"]', "john")
    page.fill('input[name="password"]', "demo")
    page.click('input[value="Log In"]')
    page.wait_for_load_state("networkidle", timeout=TIMEOUT)
    return page
