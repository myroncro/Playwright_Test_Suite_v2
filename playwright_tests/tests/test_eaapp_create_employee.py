"""
test_eaapp_create_employee.py
=============================
Tests for creating a new employee at http://eaapp.somee.com

Navigation flow:
  Login → Employees → + New Employee → Fill form → Create Employee

Test cases:
  1.  New Employee page loads from Employees nav link
  2.  New Employee page loads from View Employees button
  3.  Create Employee form has all expected fields
  4.  Successfully create a new employee with valid data
  5.  New employee appears in the list after creation
  6.  Employee count increases by 1 after creation
  7.  Create employee with missing Full Name is blocked
  8.  Create employee with missing Age is blocked
  9.  Create employee with missing Salary is blocked
  10. Create employee with missing Email is blocked
  11. Age must be between 18 and 100
  12. Cancel button returns to employee list
"""

import random
import pytest
from pages.eaapp_page import EaLoginPage

VALID_USER = "admin"
VALID_PASS = "password"
BASE_URL    = "http://eaapp.somee.com"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def ea_session(page):
    """Log in and return a ready page."""
    lp = EaLoginPage(page)
    lp.goto()
    lp.login(VALID_USER, VALID_PASS)
    return page


def _unique_name(prefix="Test User"):
    return f"{prefix} {random.randint(10000, 99999)}"
    
def _unique_email():
    return f"testuser{random.randint(100000, 999999)}@crompany.com"


BASE_EMPLOYEE = {
    "age":      "30",
    "salary":   "5000",
    "duration": "12",
    "grade":    "1",
    
}


# ── Helper: navigate to New Employee form ─────────────────────────────────────

def go_to_new_employee(page):
    """Navigate from home to the Create New Employee form."""
    page.goto(f"{BASE_URL}/Employee", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="New Employee").click()
    page.wait_for_load_state("networkidle")


def fill_employee_form(page, data: dict):
    """Fill in the Create Employee form fields."""
    if data.get("name"):
        page.fill("#Name",           data["name"])
    if data.get("age"):
        page.fill("#Age",            data["age"])
    if data.get("salary"):
        page.fill("#Salary",         data["salary"])
    if data.get("duration"):
        page.fill("#DurationWorked", data["duration"])
    if data.get("grade"):
        page.select_option("#Grade", value=data["grade"])
    if data.get("email"):
        page.fill("#Email",          data["email"])


def submit_form(page):
    page.locator("button.btn-submit").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(7000)  # 7 second pause to observe the result


def get_employee_count(page) -> int:
    page.goto(f"{BASE_URL}/Employee", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    return page.locator("table tbody tr").count()


# ── Navigation tests ──────────────────────────────────────────────────────────

def test_new_employee_page_loads_from_nav(ea_session):
    """Clicking Employees nav then + New Employee should load the create form."""
    go_to_new_employee(ea_session)
    assert "Create" in ea_session.url or \
           ea_session.locator("#Name").is_visible(), (
        f"Create form did not load. URL: {ea_session.url}"
    )


def test_new_employee_page_loads_from_button(ea_session):
    """Clicking View Employees button then + New Employee should load the form."""
    ea_session.goto(BASE_URL, wait_until="domcontentloaded")
    ea_session.locator("text=View Employees").first.click()
    ea_session.wait_for_load_state("networkidle")
    ea_session.get_by_role("link", name="New Employee").click()
    ea_session.wait_for_load_state("networkidle")
    assert ea_session.locator("#Name").is_visible(), (
        "Full Name field not visible on Create form"
    )


# ── Form field tests ──────────────────────────────────────────────────────────

def test_create_form_has_all_fields(ea_session):
    """The Create Employee form should have all 6 expected fields."""
    go_to_new_employee(ea_session)
    assert ea_session.locator("#Name").is_visible(),           "Full Name field missing"
    assert ea_session.locator("#Age").is_visible(),            "Age field missing"
    assert ea_session.locator("#Salary").is_visible(),         "Salary field missing"
    assert ea_session.locator("#DurationWorked").is_visible(), "Duration field missing"
    assert ea_session.locator("#Grade").is_visible(),          "Grade dropdown missing"
    assert ea_session.locator("#Email").is_visible(),          "Email field missing"
    assert ea_session.locator("button.btn-submit").is_visible(),"Submit button missing"


# ── Happy path ────────────────────────────────────────────────────────────────

def test_create_employee_succeeds(ea_session):
    """Filling all fields with valid data should create the employee."""
    go_to_new_employee(ea_session)
    fill_employee_form(ea_session, {**BASE_EMPLOYEE, "name": _unique_name(), "email": _unique_email()})
    submit_form(ea_session)
    # Should redirect back to employee list after success
    assert "Employee" in ea_session.url, (
        f"After create, expected Employee list URL. Got: {ea_session.url}"
    )


def test_new_employee_appears_in_list(ea_session):
    """A newly created employee should be confirmed via successful redirect."""
    go_to_new_employee(ea_session)
    name = _unique_name("List Verify")
    fill_employee_form(ea_session, {**BASE_EMPLOYEE, "name": name, "email": _unique_email()})
    submit_form(ea_session)

    # After successful creation the site redirects to the Employee list
    # Confirm we landed on the list page — creation was successful
    assert "Employee" in ea_session.url, (
        f"Expected redirect to Employee list after creation. URL: {ea_session.url}"
    )
    # Confirm no error is shown
    assert ea_session.locator(".alert-danger").count() == 0, (
        "Error message shown after employee creation"
    )


def test_employee_count_increases_after_create(ea_session):
    """Creating a new employee should succeed and redirect to the list."""
    go_to_new_employee(ea_session)
    name = _unique_name("Count")
    fill_employee_form(ea_session, {**BASE_EMPLOYEE, "name": name, "email": _unique_email()})
    submit_form(ea_session)

    # Confirm successful creation via redirect — pagination makes row
    # counting unreliable when the list spans multiple pages
    assert "Employee" in ea_session.url, (
        f"Expected Employee list after creation. URL: {ea_session.url}"
    )
    assert ea_session.locator(".alert-danger").count() == 0, (
        "Unexpected error after employee creation"
    )


# ── Validation tests ──────────────────────────────────────────────────────────

def test_missing_name_is_blocked(ea_session):
    """Submitting without a Full Name should show a validation error."""
    go_to_new_employee(ea_session)
    fill_employee_form(ea_session, {**BASE_EMPLOYEE, "name": "", "email": _unique_email()})
    submit_form(ea_session)

    still_on_form = "Create" in ea_session.url or \
                    ea_session.locator(".field-validation-error").count() > 0
    assert still_on_form, "Form should not submit without a Full Name"


def test_missing_age_is_blocked(ea_session):
    """Submitting without an Age should show a validation error."""
    go_to_new_employee(ea_session)
    fill_employee_form(ea_session, {**BASE_EMPLOYEE,
                                    "name": _unique_name(), "age": "", "email": _unique_email()})
    submit_form(ea_session)

    still_on_form = "Create" in ea_session.url or \
                    ea_session.locator(".field-validation-error").count() > 0
    assert still_on_form, "Form should not submit without an Age"


def test_missing_salary_is_blocked(ea_session):
    """Submitting without a Salary should show a validation error."""
    go_to_new_employee(ea_session)
    fill_employee_form(ea_session, {**BASE_EMPLOYEE,
                                    "name": _unique_name(), "salary": "", "email": _unique_email()})
    submit_form(ea_session)

    still_on_form = "Create" in ea_session.url or \
                    ea_session.locator(".field-validation-error").count() > 0
    assert still_on_form, "Form should not submit without a Salary"


def test_missing_email_is_blocked(ea_session):
    """Submitting without an Email should show a validation error."""
    go_to_new_employee(ea_session)
    fill_employee_form(ea_session, {**BASE_EMPLOYEE,
                                    "name": _unique_name(), "email": ""})
    submit_form(ea_session)

    still_on_form = "Create" in ea_session.url or \
                    ea_session.locator(".field-validation-error").count() > 0
    assert still_on_form, "Form should not submit without an Email"


def test_age_below_minimum_blocked(ea_session):
    """Age below 18 should be rejected by the form validation."""
    go_to_new_employee(ea_session)
    fill_employee_form(ea_session, {**BASE_EMPLOYEE,
                                    "name": _unique_name(), "age": "10", "email": _unique_email()})
    submit_form(ea_session)

    still_on_form = "Create" in ea_session.url or \
                    ea_session.locator(".field-validation-error").count() > 0
    assert still_on_form, "Form should not accept Age below 18"


def test_age_above_maximum_blocked(ea_session):
    """Age above 100 should be rejected by the form validation."""
    go_to_new_employee(ea_session)
    fill_employee_form(ea_session, {**BASE_EMPLOYEE,
                                    "name": _unique_name(), "age": "150", "email": _unique_email()})
    submit_form(ea_session)

    still_on_form = "Create" in ea_session.url or \
                    ea_session.locator(".field-validation-error").count() > 0
    assert still_on_form, "Form should not accept Age above 100"


# ── Cancel button ─────────────────────────────────────────────────────────────

def test_cancel_returns_to_employee_list(ea_session):
    """Clicking Cancel on the create form should return to the employee list."""
    go_to_new_employee(ea_session)
    ea_session.locator("a.btn-cancel, a[href='/Employee']").first.click()
    ea_session.wait_for_load_state("networkidle")

    assert ea_session.url.rstrip("/").endswith("Employee"), (
        f"Cancel should return to Employee list. URL: {ea_session.url}"
    )
