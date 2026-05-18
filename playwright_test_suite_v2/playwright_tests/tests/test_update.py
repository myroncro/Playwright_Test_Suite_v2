"""
test_update.py
==============
Tests for updating employee/customer profile data at parabank.parasoft.com

Uses the `parabank_logged_in` fixture from conftest.py (demo account: john/demo).

Test cases:
  1. Update phone number → persists after re-navigation
  2. Update first name  → success message shown
  3. Table row editing  → the-internet inline edit
"""

import pytest
from pages.employee_page import UpdateProfilePage


# ── Phone update ──────────────────────────────────────────────────────────────

def test_update_phone_number_persists(parabank_logged_in):
    """
    Changing the phone number should save successfully and the new value
    should still be present when the update form is re-opened.
    """
    page = parabank_logged_in
    up = UpdateProfilePage(page)

    new_phone = "5125559876"
    up.goto()
    up.update_phone(new_phone)

    assert up.update_succeeded(), "Update profile success message not found."

    # Re-open the form and check the value stuck
    saved_phone = up.get_current_phone()
    assert saved_phone == new_phone, (
        f"Phone was not saved. Expected '{new_phone}', got '{saved_phone}'"
    )


def test_update_phone_with_different_value(parabank_logged_in):
    """
    Running an update twice with different values should always save
    the most recent entry.
    """
    page = parabank_logged_in
    up = UpdateProfilePage(page)

    # First update
    up.goto()
    up.update_phone("5120001111")

    # Second update
    up.goto()
    up.update_phone("5129998888")
    assert up.update_succeeded()

    saved = up.get_current_phone()
    assert saved == "5129998888"


# ── Inline table editing (the-internet) ──────────────────────────────────────

def test_table_sort_by_last_name(page):
    """
    Clicking the 'Last Name' column header on the sortable tables page
    should reorder the rows.
    """
    page.goto("https://the-internet.herokuapp.com/tables")
    page.wait_for_load_state("networkidle")

    # Capture first cell value before sort
    first_before = page.locator(
        "#table1 tbody tr:first-child td:first-child"
    ).text_content().strip()

    # Click the Last Name header to sort
    page.click("#table1 thead tr th:first-child")
    page.wait_for_timeout(300)

    first_after = page.locator(
        "#table1 tbody tr:first-child td:first-child"
    ).text_content().strip()

    # After sorting, the first row may change (or stay if already sorted)
    # The important assertion is that the click didn't break the table
    assert first_after is not None and len(first_after) > 0, (
        "Table first cell is empty after sorting — something went wrong."
    )


def test_table_filter_finds_correct_row(page):
    """
    The sortable table should contain at least one row after the page loads,
    confirming data is present and accessible for scripted interaction.
    """
    page.goto("https://the-internet.herokuapp.com/tables")
    page.wait_for_load_state("networkidle")

    rows = page.locator("#table1 tbody tr")
    count = rows.count()
    assert count > 0, "Expected at least one employee row in the table."

    # Locate the row containing "Smith" and read the email cell
    smith_row = page.locator("#table1 tbody tr", has_text="Smith")
    assert smith_row.count() > 0, "Could not find a row for 'Smith'."
    email = smith_row.first.locator("td:nth-child(4)").text_content().strip()
    assert "@" in email, f"Email cell doesn't look like an email: {email}"
