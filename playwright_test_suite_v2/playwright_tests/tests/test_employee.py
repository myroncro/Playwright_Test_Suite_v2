"""
test_employee.py
================
Tests for new employee/customer registration at parabank.parasoft.com

Test cases:
  1. Successful registration with full valid data
  2. Duplicate username is rejected
  3. Missing required field (last name) is rejected
"""

import random
import pytest
from pages.employee_page import RegisterPage


def _unique_username(prefix="emp") -> str:
    """Generate a unique username to avoid conflicts between runs."""
    return f"{prefix}_{random.randint(100000, 999999)}"


BASE_DATA = {
    "first":  "Jane",
    "last":   "Doe",
    "street": "123 Main St",
    "city":   "Austin",
    "state":  "TX",
    "zip":    "78701",
    "phone":  "5125550100",
    "ssn":    "123-45-6789",
    "password": "Test@1234",
}


# ── Happy path ────────────────────────────────────────────────────────────────

def test_register_new_employee_succeeds(page):
    """
    Filling in all required fields with valid data should complete
    registration and show a confirmation/welcome message.
    """
    rp = RegisterPage(page)
    rp.goto()

    data = {**BASE_DATA, "username": _unique_username("jane")}
    rp.register(data)

    # ParaBank shows "Welcome <username>" after success
    panel_text = rp.get_confirmation_text()
    assert data["username"] in panel_text or "Welcome" in panel_text, (
        f"Registration may have failed. Page text: {panel_text[:300]}"
    )


# ── Duplicate username ────────────────────────────────────────────────────────

def test_duplicate_username_rejected(page):
    """
    Registering a second account with the same username should fail
    and display an error — the second registration should NOT succeed.
    """
    rp = RegisterPage(page)
    shared_username = _unique_username("dup")

    # First registration — should succeed
    rp.goto()
    rp.register({**BASE_DATA, "username": shared_username})
    first_text = rp.get_confirmation_text()
    assert shared_username in first_text or "Welcome" in first_text

    # Second registration with the same username — should fail
    rp.goto()
    rp.register({**BASE_DATA, "username": shared_username})
    second_text = rp.get_confirmation_text()

    # ParaBank shows "This username already exists." on failure
    assert "already exists" in second_text.lower() or "Welcome" not in second_text


# ── Missing required field ────────────────────────────────────────────────────

def test_registration_fails_without_last_name(page):
    """
    Omitting the last name (a required field) should prevent registration
    and show a validation error on the page.
    """
    rp = RegisterPage(page)
    rp.goto()

    data = {**BASE_DATA, "username": _unique_username("nolast"), "last": ""}
    rp.register(data)

    panel_text = rp.get_confirmation_text()
    # Should NOT have reached the welcome screen
    assert "Welcome" not in panel_text, (
        "Registration should have failed without a last name."
    )
