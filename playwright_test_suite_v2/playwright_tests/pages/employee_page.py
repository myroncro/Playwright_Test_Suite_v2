"""
RegisterPage & UpdateProfilePage — Page Objects for parabank.parasoft.com
Covers new employee/customer registration and profile updates.
"""


class RegisterPage:
    URL = "https://parabank.parasoft.com/parabank/register.htm"

    def __init__(self, page):
        self.page = page

    def goto(self):
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def register(self, data: dict):
        """
        Fill and submit the registration form.

        Expected keys in `data`:
            first, last, street, city, state, zip,
            phone, ssn, username, password
        """
        self.page.fill("#customer\\.firstName",          data["first"])
        self.page.fill("#customer\\.lastName",           data["last"])
        self.page.fill("#customer\\.address\\.street",   data["street"])
        self.page.fill("#customer\\.address\\.city",     data["city"])
        self.page.fill("#customer\\.address\\.state",    data["state"])
        self.page.fill("#customer\\.address\\.zipCode",  data["zip"])
        self.page.fill("#customer\\.phoneNumber",        data["phone"])
        self.page.fill("#customer\\.ssn",                data["ssn"])
        self.page.fill("#customer\\.username",           data["username"])
        self.page.fill("#customer\\.password",           data["password"])
        self.page.fill("#repeatedPassword",              data["password"])
        self.page.click('input[value="Register"]')
        self.page.wait_for_load_state("networkidle")

    def registration_succeeded(self) -> bool:
        """Return True if the welcome/confirmation element is present."""
        return self.page.locator("h1.title, #rightPanel p").first.is_visible()

    def get_confirmation_text(self) -> str:
        return self.page.locator("#rightPanel").text_content().strip()


class UpdateProfilePage:
    URL = "https://parabank.parasoft.com/parabank/updateprofile.htm"

    def __init__(self, page):
        self.page = page

    def goto(self):
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def update_phone(self, new_phone: str):
        """Clear the phone field and enter a new number."""
        phone = self.page.locator('input[name="customer.phoneNumber"]')
        phone.triple_click()
        phone.type(new_phone)
        self.page.click('input[value="Update Profile"]')
        self.page.wait_for_load_state("networkidle")

    def get_current_phone(self) -> str:
        self.goto()
        return self.page.input_value('input[name="customer.phoneNumber"]')

    def update_succeeded(self) -> bool:
        heading = self.page.locator("h1.title, #rightPanel p").first
        return "Updated" in heading.text_content() or heading.is_visible()
