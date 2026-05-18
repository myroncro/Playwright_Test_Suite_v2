"""
LoginPage — Page Object for the-internet.herokuapp.com/login
Encapsulates all selectors and actions for the login screen.
"""


class LoginPage:
    URL = "https://the-internet.herokuapp.com/login"

    def __init__(self, page):
        self.page = page
        # Locators
        self.username_field = page.locator("#username")
        self.password_field = page.locator("#password")
        self.submit_button  = page.locator('button[type="submit"]')
        self.flash_message  = page.locator("#flash")
        self.page_heading   = page.locator("h2")

    # ── Actions ──────────────────────────────────────────────────────────────

    def goto(self):
        """Navigate to the login page."""
        self.page.goto(self.URL)

    def login(self, username: str, password: str):
        """Fill credentials and submit the login form."""
        self.username_field.fill(username)
        self.password_field.fill(password)
        self.submit_button.click()

    # ── Assertions / helpers ─────────────────────────────────────────────────

    def is_on_secure_page(self) -> bool:
        return self.page.url.endswith("/secure")

    def get_flash_text(self) -> str:
        return self.flash_message.text_content().strip()

    def flash_is_visible(self) -> bool:
        return self.flash_message.is_visible()
