"""
test_login.py
=============
Tests for the login form at the-internet.herokuapp.com/login

Test cases:
  1. Valid credentials → lands on /secure
  2. Wrong username    → flash error shown
  3. Wrong password    → flash error shown
  4. Empty username    → flash error shown
  5. Empty password    → flash error shown
  6. Both empty        → flash error shown
"""

import pytest
from pages.login_page import LoginPage

VALID_USER = "tomsmith"
VALID_PASS = "SuperSecretPassword!"


# ── Happy path ────────────────────────────────────────────────────────────────

def test_valid_login_redirects_to_secure(page):
    """Logging in with correct credentials should land on /secure."""
    lp = LoginPage(page)
    lp.goto()
    lp.login(VALID_USER, VALID_PASS)

    assert lp.is_on_secure_page(), f"Expected /secure, got: {page.url}"
    assert "Secure Area" in page.locator("h2").text_content()


def test_valid_login_shows_success_flash(page):
    """A green flash message should appear after a successful login."""
    lp = LoginPage(page)
    lp.goto()
    lp.login(VALID_USER, VALID_PASS)

    assert "You logged into a secure area" in lp.get_flash_text()


# ── Invalid credentials ───────────────────────────────────────────────────────

def test_wrong_username_shows_error(page):
    """An invalid username should display an error flash, not log in."""
    lp = LoginPage(page)
    lp.goto()
    lp.login("totally_wrong_user", VALID_PASS)

    assert not lp.is_on_secure_page()
    assert "Your username is invalid" in lp.get_flash_text()


def test_wrong_password_shows_error(page):
    """A correct username but wrong password should show an error."""
    lp = LoginPage(page)
    lp.goto()
    lp.login(VALID_USER, "wrongpassword123")

    assert not lp.is_on_secure_page()
    assert "Your password is invalid" in lp.get_flash_text()


# ── Empty fields ──────────────────────────────────────────────────────────────

def test_empty_username_shows_error(page):
    """Submitting with no username should show a validation error."""
    lp = LoginPage(page)
    lp.goto()
    lp.login("", VALID_PASS)

    assert lp.flash_is_visible()
    assert not lp.is_on_secure_page()


def test_empty_password_shows_error(page):
    """Submitting with no password should show a validation error."""
    lp = LoginPage(page)
    lp.goto()
    lp.login(VALID_USER, "")

    assert lp.flash_is_visible()
    assert not lp.is_on_secure_page()


def test_both_fields_empty_shows_error(page):
    """Submitting a completely blank form should show a validation error."""
    lp = LoginPage(page)
    lp.goto()
    lp.login("", "")

    assert lp.flash_is_visible()
    assert not lp.is_on_secure_page()
