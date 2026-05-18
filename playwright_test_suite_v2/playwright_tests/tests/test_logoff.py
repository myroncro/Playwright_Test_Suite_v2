"""
test_logoff.py
==============
Tests for logout functionality and session invalidation.

Covers both the-internet.herokuapp.com and parabank.parasoft.com.

Test cases:
  1. Logout redirects to login page (the-internet)
  2. Flash message confirms logout (the-internet)
  3. Session is invalidated — direct URL access after logout redirects (the-internet)
  4. ParaBank logout redirects to login
  5. ParaBank session invalidated after logout
"""

import pytest
from pages.login_page import LoginPage


# ── the-internet logout ───────────────────────────────────────────────────────

def test_logout_redirects_to_login_page(logged_in_page):
    """
    Clicking Logout from the secure area should send the user back to /login.
    """
    page = logged_in_page
    assert page.url.endswith("/secure"), "Fixture didn't land on /secure"

    page.click("text=Logout")
    page.wait_for_url("**/login")

    assert page.url.endswith("/login"), f"Expected /login, got: {page.url}"


def test_logout_shows_confirmation_flash(logged_in_page):
    """
    A flash message should confirm the user has been logged out.
    """
    page = logged_in_page
    page.click("text=Logout")
    page.wait_for_url("**/login")

    flash = page.locator("#flash").text_content().strip()
    assert "logged out" in flash.lower(), (
        f"Expected 'logged out' in flash, got: '{flash}'"
    )


def test_session_invalidated_after_logout(logged_in_page):
    """
    After logging out, navigating directly to /secure should NOT succeed —
    the app must redirect away (session cookie should be invalidated).
    """
    page = logged_in_page
    page.click("text=Logout")
    page.wait_for_url("**/login")

    # Attempt to bypass logout by going straight to the protected page
    page.goto("https://the-internet.herokuapp.com/secure")
    page.wait_for_load_state("networkidle")

    assert not page.url.endswith("/secure"), (
        "User was able to access /secure after logout — session not invalidated!"
    )


def test_login_page_accessible_after_logout(logged_in_page):
    """
    The login form should be fully functional immediately after logout
    (fields and button should all be present and interactable).
    """
    page = logged_in_page
    page.click("text=Logout")
    page.wait_for_url("**/login")

    lp = LoginPage(page)
    assert lp.username_field.is_visible(), "Username field not visible after logout"
    assert lp.password_field.is_visible(), "Password field not visible after logout"
    assert lp.submit_button.is_visible(), "Submit button not visible after logout"


# ── ParaBank logout ───────────────────────────────────────────────────────────

def test_parabank_logout_redirects(parabank_logged_in):
    """
    Logging out of ParaBank should redirect to the login page.
    """
    page = parabank_logged_in

    logout_link = page.locator("a[href*='logout'], text=Log Out")
    assert logout_link.count() > 0, "Logout link not found — may not be logged in"
    logout_link.first.click()
    page.wait_for_load_state("networkidle")

    assert "login" in page.url.lower() or page.locator('input[name="username"]').is_visible(), (
        f"Did not end up on login page after logout. URL: {page.url}"
    )


def test_parabank_session_cleared_after_logout(parabank_logged_in):
    """
    Navigating to a protected ParaBank page after logout should redirect
    back to login — not show account data.
    """
    page = parabank_logged_in

    logout_link = page.locator("a[href*='logout'], text=Log Out")
    logout_link.first.click()
    page.wait_for_load_state("networkidle")

    # Try to access the accounts overview directly
    page.goto("https://parabank.parasoft.com/parabank/accounts.htm")
    page.wait_for_load_state("networkidle")

    # Should be redirected to login — not see account data
    is_on_login = (
        "login" in page.url.lower()
        or page.locator('input[name="username"]').is_visible()
    )
    assert is_on_login, (
        "Accessed accounts page after logout — session was not cleared!"
    )
