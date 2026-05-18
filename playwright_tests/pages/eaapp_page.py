"""
eaapp_page.py
=============
Page Objects for http://eaapp.somee.com

Covers:
  - LoginPage        : login / logout
  - EmployeePage     : create, edit, delete, list employees
  - DashboardPage    : verify dashboard loads after login
"""


BASE_URL = "http://eaapp.somee.com"


# ── Login Page ────────────────────────────────────────────────────────────────

class EaLoginPage:
    URL = f"{BASE_URL}/Account/LogIn"

    def __init__(self, page):
        self.page = page
        self.username_field  = page.locator("#UserName")
        self.password_field  = page.locator("#Password")
        self.submit_button   = page.locator('button.btn-signin')
        self.error_message   = page.locator(".alert-danger")

    def goto(self):
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self.username_field.wait_for(state="visible")

    def login(self, username: str, password: str):
        self.username_field.fill(username)
        self.password_field.fill(password)
        self.submit_button.click()
        self.page.wait_for_load_state("networkidle")

    def logout(self):
        self.page.locator("form[action*='Logout'] button").click()
        self.page.wait_for_load_state("networkidle")

    def is_logged_in(self) -> bool:
        return "LogIn" not in self.page.url

    def get_error_text(self) -> str:
        if self.error_message.is_visible():
            return self.error_message.text_content().strip()
        return ""


# ── Employee Page ─────────────────────────────────────────────────────────────

class EaEmployeePage:
    LIST_URL   = f"{BASE_URL}/Employee"
    CREATE_URL = f"{BASE_URL}/Employee/Create"

    def __init__(self, page):
        self.page = page

    def goto_list(self):
        self.page.goto(self.LIST_URL, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def goto_create(self):
        self.page.goto(self.CREATE_URL, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def create_employee(self, data: dict):
        """
        Fill and submit the Create Employee form.

        Expected keys:
            name, salary, duration, grade (select text), email
        """
        self.page.fill("#EmployeeName",     data["name"])
        self.page.fill("#Salary",           str(data["salary"]))
        self.page.fill("#StartDateofWork",  data["duration"])
        self.page.select_option("#EmployeeGrade", label=data["grade"])
        self.page.fill("#Email",            data["email"])
        self.page.click('input[type="submit"]')
        self.page.wait_for_load_state("networkidle")

    def employee_exists_in_list(self, name: str) -> bool:
        self.goto_list()
        return self.page.locator(f"td:has-text('{name}')").count() > 0

    def click_edit_for(self, name: str):
        """Click the Edit link on the row matching the given employee name."""
        row = self.page.locator("tr", has_text=name).first
        row.locator("text=Edit").click()
        self.page.wait_for_load_state("networkidle")

    def click_delete_for(self, name: str):
        """Click the Delete link on the row matching the given employee name."""
        row = self.page.locator("tr", has_text=name).first
        row.locator("text=Delete").click()
        self.page.wait_for_load_state("networkidle")

    def confirm_delete(self):
        """Confirm deletion on the delete confirmation page."""
        self.page.click('input[type="submit"]')
        self.page.wait_for_load_state("networkidle")

    def update_salary(self, new_salary: str):
        """Clear the salary field and enter a new value."""
        salary_field = self.page.locator("#Salary")
        salary_field.triple_click()
        salary_field.type(new_salary)
        self.page.click('input[type="submit"]')
        self.page.wait_for_load_state("networkidle")

    def get_row_count(self) -> int:
        """Return number of employee rows in the list table."""
        return self.page.locator("table tbody tr").count()


# ── Dashboard Page ────────────────────────────────────────────────────────────

class EaDashboardPage:
    URL = f"{BASE_URL}/Dashboard"

    def __init__(self, page):
        self.page = page

    def goto(self):
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def is_loaded(self) -> bool:
        return self.page.locator("body").is_visible()
