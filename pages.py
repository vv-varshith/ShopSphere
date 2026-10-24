# ============================================================
#  SauceDemo Automation - Page Object Models
#  Tester: Varshith Vasamsetti
# ============================================================

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


# ---------- Base Page ----------

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def find(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def click(self, by, value):
        el = self.wait.until(EC.element_to_be_clickable((by, value)))
        el.click()

    def type_text(self, by, value, text):
        el = self.find(by, value)
        el.clear()
        el.send_keys(text)

    def get_text(self, by, value):
        return self.find(by, value).text

    def is_visible(self, by, value):
        try:
            self.wait.until(EC.visibility_of_element_located((by, value)))
            return True
        except Exception:
            return False


# ---------- Login Page ----------

class LoginPage(BasePage):
    URL = "https://www.saucedemo.com/"

    # Locators
    USERNAME_INPUT  = (By.ID, "user-name")
    PASSWORD_INPUT  = (By.ID, "password")
    LOGIN_BUTTON    = (By.ID, "login-button")
    ERROR_MESSAGE   = (By.CSS_SELECTOR, "[data-test='error']")

    def open(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        self.type_text(*self.USERNAME_INPUT, username)
        self.type_text(*self.PASSWORD_INPUT, password)
        self.click(*self.LOGIN_BUTTON)

    def get_error(self):
        return self.get_text(*self.ERROR_MESSAGE)

    def is_error_displayed(self):
        return self.is_visible(*self.ERROR_MESSAGE)


# ---------- Inventory / Products Page ----------

class InventoryPage(BasePage):
    # Locators
    PAGE_TITLE        = (By.CLASS_NAME, "title")
    SORT_DROPDOWN     = (By.CLASS_NAME, "product_sort_container")
    PRODUCT_NAMES     = (By.CLASS_NAME, "inventory_item_name")
    PRODUCT_PRICES    = (By.CLASS_NAME, "inventory_item_price")
    ADD_TO_CART_BTN   = (By.XPATH, "(//button[contains(@id,'add-to-cart')])[1]")
    CART_BADGE        = (By.CLASS_NAME, "shopping_cart_badge")
    CART_ICON         = (By.CLASS_NAME, "shopping_cart_link")
    BURGER_MENU       = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK       = (By.ID, "logout_sidebar_link")

    def get_page_title(self):
        return self.get_text(*self.PAGE_TITLE)

    def sort_products(self, sort_value):
        """sort_value: 'az', 'za', 'lohi', 'hilo'"""
        dropdown = Select(self.find(*self.SORT_DROPDOWN))
        dropdown.select_by_value(sort_value)

    def get_product_names(self):
        elements = self.driver.find_elements(*self.PRODUCT_NAMES)
        return [el.text for el in elements]

    def get_product_prices(self):
        elements = self.driver.find_elements(*self.PRODUCT_PRICES)
        return [float(el.text.replace("$", "")) for el in elements]

    def add_first_product_to_cart(self):
        el = self.wait.until(EC.presence_of_element_located(self.ADD_TO_CART_BTN))
        self.driver.execute_script("arguments[0].click();", el)
        time.sleep(1)

    def add_product_by_name(self, product_name):
        btn_id = "add-to-cart-" + product_name.lower().replace(" ", "-")
        # Use JavaScript click for reliability
        el = self.wait.until(EC.presence_of_element_located((By.ID, btn_id)))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", el)
        # Wait until cart badge appears or count increases
        time.sleep(1)

    def get_cart_count(self):
        try:
            # Wait up to 5 seconds for badge to appear
            badge = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.CART_BADGE)
            )
            return int(badge.text)
        except Exception:
            return 0

    def go_to_cart(self):
        el = self.wait.until(EC.element_to_be_clickable(self.CART_ICON))
        self.driver.execute_script("arguments[0].click();", el)
        # Wait for cart page to fully load
        time.sleep(2)

    def logout(self):
        # Click burger menu and wait for it to open
        burger = self.wait.until(EC.element_to_be_clickable(self.BURGER_MENU))
        self.driver.execute_script("arguments[0].click();", burger)
        time.sleep(1.5)  # wait for sidebar animation
        # Wait for logout link to be visible then click
        logout = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.LOGOUT_LINK)
        )
        self.driver.execute_script("arguments[0].click();", logout)
        time.sleep(1)


# ---------- Cart Page ----------

class CartPage(BasePage):
    PAGE_TITLE        = (By.CLASS_NAME, "title")
    CART_ITEMS        = (By.CLASS_NAME, "cart_item")
    ITEM_NAMES        = (By.CLASS_NAME, "inventory_item_name")
    REMOVE_BUTTON     = (By.XPATH, "(//button[contains(@id,'remove')])[1]")
    CHECKOUT_BUTTON   = (By.ID, "checkout")
    CONTINUE_SHOPPING = (By.ID, "continue-shopping")

    def get_cart_items(self):
        return self.driver.find_elements(*self.CART_ITEMS)

    def get_item_names(self):
        elements = self.driver.find_elements(*self.ITEM_NAMES)
        return [el.text for el in elements]

    def remove_first_item(self):
        self.click(*self.REMOVE_BUTTON)

    def proceed_to_checkout(self):
        el = self.wait.until(EC.presence_of_element_located(self.CHECKOUT_BUTTON))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", el)
        time.sleep(1)

    def continue_shopping(self):
        self.click(*self.CONTINUE_SHOPPING)


# ---------- Checkout Step One ----------

class CheckoutStepOnePage(BasePage):
    FIRST_NAME  = (By.ID, "first-name")
    LAST_NAME   = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE    = (By.ID, "continue")
    ERROR_MSG   = (By.CSS_SELECTOR, "[data-test='error']")

    def fill_form(self, first, last, postal):
        self.type_text(*self.FIRST_NAME, first)
        self.type_text(*self.LAST_NAME, last)
        self.type_text(*self.POSTAL_CODE, postal)

    def continue_checkout(self):
        self.click(*self.CONTINUE)

    def get_error(self):
        return self.get_text(*self.ERROR_MSG)


# ---------- Checkout Step Two (Overview) ----------

class CheckoutStepTwoPage(BasePage):
    ITEM_TOTAL  = (By.CLASS_NAME, "summary_subtotal_label")
    TAX         = (By.CLASS_NAME, "summary_tax_label")
    TOTAL       = (By.CLASS_NAME, "summary_total_label")
    FINISH_BTN  = (By.ID, "finish")

    def get_item_total(self):
        return self.get_text(*self.ITEM_TOTAL)

    def get_total(self):
        return self.get_text(*self.TOTAL)

    def finish_order(self):
        self.click(*self.FINISH_BTN)


# ---------- Order Confirmation Page ----------

class OrderConfirmationPage(BasePage):
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    COMPLETE_TEXT   = (By.CLASS_NAME, "complete-text")
    BACK_HOME_BTN   = (By.ID, "back-to-products")

    def get_confirmation_header(self):
        return self.get_text(*self.COMPLETE_HEADER)

    def get_confirmation_text(self):
        return self.get_text(*self.COMPLETE_TEXT)

    def go_back_home(self):
        self.click(*self.BACK_HOME_BTN)
