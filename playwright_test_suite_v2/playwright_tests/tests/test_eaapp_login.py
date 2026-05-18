"""
test_eaapp_login.py
===================
Login tests for http://eaapp.somee.com

Test cases:
  1.  Valid login redirects away from login page
  2.  Valid login shows nav menu items (Home, Employees etc.)
  3.  Valid login shows View Employees button
  4.  Invalid username shows error message
  5.  Invalid password shows error message
  6.  Empty username is blocked
  7.  Empty password is blocked
  8.  Both fields empty is blocked
  9.  Login page is accessible without being logged in
  10. Logout redirects back to home page
  11. Logout shows login link again (session ended)
"""

import pytest
from pages.eaapp_page import EaLoginPage, EaEmployeePage

VALID_USER = "admin"
VALID_PASS = "password"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def login_page(page):
    lp = EaLoginPage(page)
    lp.goto()
    return lp


@pytest.fixture
def logged_in_ea(page):
    """Return a page already logged in to eaapp."""
    lp = EaLoginPage(page)
    lp.goto()
    lp.login(VALID_USER, VALID_PASS)
    return page


# ── Happy path ────────────────────────────────────────────────────────────────

def test_valid_login_leaves_login_page(login_page, page):
    """Correct credentials should navigate away from the login page."""
    login_page.login(VALID_USER, VALID_PASS)
    assert "LogIn" not in page.url, (
        f"Still on login page after valid login. URL: {page.url}"
    )


def test_valid_login_shows_nav_menu(login_page, page):
    """After login the top nav should show Home and Employees nav links."""
    login_page.login(VALID_USER, VALID_PASS)
    # Use href-based selectors to avoid matching multiple elements with 'Employee' text
    assert page.locator("a.nav-link[href='/']").is_visible(), \
        "Home nav link not found"
    assert page.locator("a.nav-link[href='/Employee']").is_visible(), \
        "Employees nav link not found"
    # Logout link — try common variations
    logout = page.locator("a[href*='Logout'], a[href*='LogOff']").first
    assert logout.is_visible(), "Logout link not found in nav"


def test_valid_login_shows_view_employees_button(login_page, page):
    """The home page should show the View Employees button after login."""
    login_page.login(VALID_USER, VALID_PASS)
    btn = page.locator("text=View Employees").first
    assert btn.is_visible(), "View Employees button not visible after login"


# ── Invalid credentials ───────────────────────────────────────────────────────

def test_invalid_username_shows_error(login_page, page):
    """A wrong username should show an error message on the page."""
    login_page.login("wronguser123", VALID_PASS)
    error = page.locator(".alert-danger")
    assert error.is_visible(), "Expected error message for invalid username"
    assert len(error.text_content().strip()) > 0, "Error message is empty"


def test_invalid_password_shows_error(login_page, page):
    """A wrong password should show an error message on the page."""
    login_page.login(VALID_USER, "wrongpassword999")
    error = page.locator(".alert-danger")
    assert error.is_visible(), "Expected error message for invalid password"
    assert len(error.text_content().strip()) > 0, "Error message is empty"


# ── Empty fields ──────────────────────────────────────────────────────────────

def test_empty_username_blocked(login_page, page):
    """Submitting with no username should not log in."""
    login_page.login("", VALID_PASS)
    assert "LogIn" in page.url or page.locator(".alert-danger").is_visible(), \
        "Should not log in with empty username"


def test_empty_password_blocked(login_page, page):
    """Submitting with no password should not log in."""
    login_page.login(VALID_USER, "")
    assert "LogIn" in page.url or page.locator(".alert-danger").is_visible(), \
        "Should not log in with empty password"


def test_both_fields_empty_blocked(login_page, page):
    """Submitting a blank form should not log in."""
    login_page.login("", "")
    assert "LogIn" in page.url or page.locator(".alert-danger").is_visible(), \
        "Should not log in with empty credentials"


# ── Page access ───────────────────────────────────────────────────────────────

def test_login_page_accessible_without_auth(page):
    """The login page should be reachable without any credentials."""
    lp = EaLoginPage(page)
    lp.goto()
    assert lp.username_field.is_visible(), "Username field not visible"
    assert lp.password_field.is_visible(), "Password field not visible"
    assert lp.submit_button.is_visible(),  "Submit button not visible"


# ── Logout ────────────────────────────────────────────────────────────────────

def test_logout_returns_to_home_page(logged_in_ea):
    """
    Clicking Logout should redirect to the home/root page
    and the login link should be visible again.
    """
    page = logged_in_ea
    lp = EaLoginPage(page)
    lp.logout()

    # After logout this site redirects to home (/) not /LogIn
    assert page.url.rstrip("/") == "http://eaapp.somee.com" or \
           "LogIn" in page.url, (
        f"Did not return to home or login page after logout. URL: {page.url}"
    )


def test_login_link_visible_after_logout(logged_in_ea):
    """
    After logging out the Login nav link should be visible,
    confirming the session has ended.
    """
    page = logged_in_ea
    lp = EaLoginPage(page)
    lp.logout()

    # After logout the Login link should appear in the nav
    login_link = page.locator("a[href*='LogIn'], a[href*='Login']").first
    assert login_link.is_visible(), (
        "Login link not visible after logout — may still be logged in"
    )