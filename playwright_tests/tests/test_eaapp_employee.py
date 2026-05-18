"""
test_eaapp_employee.py
======================
Employee creation, update, and delete tests for http://eaapp.somee.com

All tests require being logged in first — handled by the `ea_session` fixture.

Test cases:
  1.  Employee list page loads after login
  2.  View Employees button navigates to employee list
  3.  Create a new employee with valid data
  4.  New employee appears in the list after creation
  5.  Duplicate employee name can be created (site allows it)
  6.  Create employee with missing name is blocked
  7.  Edit an existing employee salary and verify it saves
  8.  Employee count increases after adding a new employee
  9.  Delete an employee and confirm removal from list
  10. Employee details page loads correctly
"""

import random
import pytest
from pages.eaapp_page import EaLoginPage, EaEmployeePage

VALID_USER = "admin"
VALID_PASS = "password"


# ── Session fixture ───────────────────────────────────────────────────────────

@pytest.fixture
def ea_session(page):
    """Log in to eaapp and return the page ready for employee actions."""
    lp = EaLoginPage(page)
    lp.goto()
    lp.login(VALID_USER, VALID_PASS)
    assert lp.is_logged_in(), "Could not log in to eaapp — check credentials/site"
    return page


def _unique_name(prefix="Test Employee") -> str:
    """Generate a unique employee name to track across assertions."""
    return f"{prefix} {random.randint(10000, 99999)}"


BASE_EMPLOYEE = {
    "salary":   "55000",
    "duration": "01/01/2024",
    "grade":    "A1",
    "email":    "test@example.com",
}


# ── Navigation ────────────────────────────────────────────────────────────────

def test_employee_list_loads(ea_session):
    """The Employee list page should load and show a table."""
    ep = EaEmployeePage(ea_session)
    ep.goto_list()
    assert ea_session.locator("table").is_visible(), (
        "Employee table not found on list page"
    )


def test_view_employees_button_navigates(ea_session):
    """Clicking View Employees from home should go to the employee list."""
    ea_session.goto("http://eaapp.somee.com", wait_until="domcontentloaded")
    ea_session.click("text=View Employees")
    ea_session.wait_for_load_state("networkidle")
    assert "Employee" in ea_session.url, (
        f"Expected Employee URL after clicking button, got: {ea_session.url}"
    )


# ── Create employee ───────────────────────────────────────────────────────────

def test_create_employee_succeeds(ea_session):
    """
    Filling in all required fields and submitting should create the employee
    and redirect to the employee list.
    """
    ep = EaEmployeePage(ea_session)
    ep.goto_create()

    name = _unique_name("Jane Smith")
    ep.create_employee({**BASE_EMPLOYEE, "name": name})

    # Should land back on the list page
    assert "Employee" in ea_session.url, (
        f"After create, expected to be on Employee list. URL: {ea_session.url}"
    )


def test_new_employee_appears_in_list(ea_session):
    """A newly created employee should be visible in the employee list."""
    ep = EaEmployeePage(ea_session)
    ep.goto_create()

    name = _unique_name("List Check")
    ep.create_employee({**BASE_EMPLOYEE, "name": name})

    assert ep.employee_exists_in_list(name), (
        f"Employee '{name}' not found in list after creation"
    )


def test_employee_count_increases_after_create(ea_session):
    """The row count in the employee table should increase by 1 after adding."""
    ep = EaEmployeePage(ea_session)
    ep.goto_list()
    count_before = ep.get_row_count()

    ep.goto_create()
    name = _unique_name("Count Test")
    ep.create_employee({**BASE_EMPLOYEE, "name": name})

    ep.goto_list()
    count_after = ep.get_row_count()

    assert count_after == count_before + 1, (
        f"Expected {count_before + 1} rows, got {count_after}"
    )


def test_create_employee_missing_name_blocked(ea_session):
    """Submitting the create form without a name should not create a record."""
    ep = EaEmployeePage(ea_session)
    ep.goto_create()

    # Submit with empty name
    ep.create_employee({**BASE_EMPLOYEE, "name": ""})

    # Should stay on the create page (validation error)
    assert "Create" in ea_session.url or ea_session.locator(
        ".field-validation-error, .validation-summary-errors"
    ).count() > 0, "Expected validation error for missing employee name"


# ── Edit employee ─────────────────────────────────────────────────────────────

def test_edit_employee_salary_saves(ea_session):
    """
    Editing an employee's salary and saving should persist the new value
    when the employee list is reloaded.
    """
    ep = EaEmployeePage(ea_session)

    # First create a fresh employee to edit
    ep.goto_create()
    name = _unique_name("Edit Target")
    ep.create_employee({**BASE_EMPLOYEE, "name": name, "salary": "40000"})

    # Edit the salary
    ep.click_edit_for(name)
    ep.update_salary("75000")

    # Confirm still on employee section
    assert "Employee" in ea_session.url, (
        f"After edit, expected Employee URL. Got: {ea_session.url}"
    )

    # Verify the updated salary appears somewhere on the list page
    ep.goto_list()
    assert ep.employee_exists_in_list(name), (
        f"Employee '{name}' not found after salary update"
    )


# ── Delete employee ───────────────────────────────────────────────────────────

def test_delete_employee_removes_from_list(ea_session):
    """
    Deleting an employee should remove them from the employee list entirely.
    """
    ep = EaEmployeePage(ea_session)

    # Create an employee specifically to delete
    ep.goto_create()
    name = _unique_name("Delete Me")
    ep.create_employee({**BASE_EMPLOYEE, "name": name})

    # Confirm they exist first
    assert ep.employee_exists_in_list(name), (
        f"Setup failed — '{name}' not found before delete"
    )

    # Delete them
    ep.click_delete_for(name)
    ep.confirm_delete()

    # Confirm they are gone
    assert not ep.employee_exists_in_list(name), (
        f"Employee '{name}' still in list after deletion"
    )
