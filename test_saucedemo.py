import os
import time
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config

from pages import (
    LoginPage,
    InventoryPage,
    CartPage,
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
    OrderConfirmationPage,
)


# ==========================================================
# SAUCEDEMO AUTOMATION - SHOPSPHERE
# Website: https://www.saucedemo.com/
# Test Cases: TC01 to TC08
# Screenshots: screenshots/
# ==========================================================

WAIT_TIME = 25
STEP_DELAY = 1.5


def pause(seconds=STEP_DELAY):
    """Slow down actions so they are visible in the browser."""
    time.sleep(seconds)


def save_screenshot(driver, filename):
    """Save a screenshot inside the screenshots folder."""
    os.makedirs("screenshots", exist_ok=True)
    path = os.path.join("screenshots", filename)

    saved = driver.save_screenshot(path)

    if saved:
        print(f"Screenshot saved: {path}")
    else:
        print(f"Screenshot could not be saved: {path}")

    return saved


def wait_for_url(driver, text):
    WebDriverWait(driver, WAIT_TIME).until(
        EC.url_contains(text)
    )


def do_login(driver, username=None, password=None):
    """Log in and return the InventoryPage object."""

    if username is None:
        username = config.USERNAME

    if password is None:
        password = config.PASSWORD

    login_page = LoginPage(driver)

    login_page.open()
    pause()

    login_page.type_text(
        *LoginPage.USERNAME_INPUT,
        username
    )
    pause(0.7)

    login_page.type_text(
        *LoginPage.PASSWORD_INPUT,
        password
    )
    pause(0.7)

    login_page.click(*LoginPage.LOGIN_BUTTON)

    wait_for_url(driver, "inventory.html")
    pause()

    return InventoryPage(driver)


def add_product_and_verify(driver, product_id):
    """Add one product and verify that the cart count increases."""

    inventory = InventoryPage(driver)

    inventory.add_product_by_name(product_id)

    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: inventory.get_cart_count() >= 1
    )

    pause()
    return inventory


def open_cart(driver):
    """Open the shopping cart and return its page object."""

    inventory = InventoryPage(driver)
    inventory.go_to_cart()

    wait_for_url(driver, "cart.html")
    pause()

    return CartPage(driver)


# ==========================================================
# TC01 - VALID LOGIN
# ==========================================================

def test_tc01_valid_login(driver):
    print("\n========== TC01: VALID LOGIN ==========")

    login_page = LoginPage(driver)
    login_page.open()
    pause()

    login_page.type_text(
        *LoginPage.USERNAME_INPUT,
        config.USERNAME
    )
    pause()

    login_page.type_text(
        *LoginPage.PASSWORD_INPUT,
        config.PASSWORD
    )
    pause()

    login_page.click(*LoginPage.LOGIN_BUTTON)

    wait_for_url(driver, "inventory.html")

    inventory = InventoryPage(driver)
    title = inventory.get_page_title()

    print("Page title:", title)

    assert title == "Products", (
        f"Expected Products page, but received: {title}"
    )

    print("TC01 PASSED")


# ==========================================================
# TC02 - INVALID LOGIN
# ==========================================================

def test_tc02_invalid_login(driver):
    print("\n========== TC02: INVALID LOGIN ==========")

    login_page = LoginPage(driver)
    login_page.open()
    pause()

    login_page.type_text(
        *LoginPage.USERNAME_INPUT,
        "standard_user"
    )
    pause()

    login_page.type_text(
        *LoginPage.PASSWORD_INPUT,
        "wrongpassword"
    )
    pause()

    login_page.click(*LoginPage.LOGIN_BUTTON)
    pause()

    assert login_page.is_error_displayed(), (
        "Expected an error message for invalid login."
    )

    error_text = login_page.get_error()

    print("Error message:", error_text)

    assert "do not match" in error_text.lower() or (
        "epic sadface" in error_text.lower()
    ), f"Unexpected login error: {error_text}"

    print("TC02 PASSED")


# ==========================================================
# TC03 - PRODUCT SORTING
# ==========================================================

def test_tc03_product_sorting(driver):
    print("\n========== TC03: PRODUCT SORTING ==========")

    inventory = do_login(driver)

    # A to Z
    inventory.sort_products("az")
    pause()

    names_az = inventory.get_product_names()

    assert names_az == sorted(names_az), (
        "Product sorting A-Z failed."
    )

    print("A-Z sorting passed")

    # Z to A
    inventory.sort_products("za")
    pause()

    names_za = inventory.get_product_names()

    assert names_za == sorted(names_za, reverse=True), (
        "Product sorting Z-A failed."
    )

    print("Z-A sorting passed")

    # Price low to high
    inventory.sort_products("lohi")
    pause()

    prices_low_high = inventory.get_product_prices()

    assert prices_low_high == sorted(prices_low_high), (
        "Price low-to-high sorting failed."
    )

    print("Price low-to-high sorting passed")

    # Price high to low
    inventory.sort_products("hilo")
    pause()

    prices_high_low = inventory.get_product_prices()

    assert prices_high_low == sorted(
        prices_high_low,
        reverse=True
    ), "Price high-to-low sorting failed."

    print("Price high-to-low sorting passed")
    print("TC03 PASSED")


# ==========================================================
# TC04 - ADD MULTIPLE PRODUCTS TO CART
# ==========================================================

def test_tc04_add_to_cart(driver):
    print("\n========== TC04: ADD PRODUCTS TO CART ==========")

    inventory = do_login(driver)

    # Add first product
    inventory.add_product_by_name("sauce-labs-backpack")
    pause()

    count = inventory.get_cart_count()

    assert count == 1, (
        f"Expected 1 product in cart, got {count}"
    )

    print("Backpack added successfully")

    # Add second product
    inventory.add_product_by_name("sauce-labs-bike-light")
    pause()

    count = inventory.get_cart_count()

    assert count == 2, (
        f"Expected 2 products in cart, got {count}"
    )

    print("Bike Light added successfully")
    print("TC04 PASSED")


# ==========================================================
# TC05 - REMOVE PRODUCT FROM CART
# ==========================================================

def test_tc05_remove_from_cart(driver):
    print("\n========== TC05: REMOVE PRODUCT FROM CART ==========")

    inventory = do_login(driver)

    # Add a product
    inventory.add_product_by_name("sauce-labs-backpack")
    pause()

    assert inventory.get_cart_count() == 1, (
        "Product was not added to the cart."
    )

    # Open cart
    cart = open_cart(driver)

    # Verify product exists before removal
    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: len(cart.get_cart_items()) == 1
    )

    items_before = cart.get_item_names()

    print("Before removal:", items_before)

    assert "Sauce Labs Backpack" in items_before, (
        "Backpack was not found in the cart."
    )

    # Screenshot before removal
    save_screenshot(driver, "TC05_BEFORE_REMOVE.png")

    pause()

    # Remove product
    cart.remove_first_item()

    # Wait until cart becomes empty
    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: len(cart.get_cart_items()) == 0
    )

    pause()

    items_after = cart.get_item_names()

    print("After removal:", items_after)

    assert len(items_after) == 0, (
        f"Cart should be empty, but found: {items_after}"
    )

    # Screenshot after removal
    save_screenshot(driver, "TC05_AFTER_REMOVE.png")

    print("TC05 PASSED")


# ==========================================================
# TC06 - COMPLETE CHECKOUT / PLACE ORDER
# ==========================================================

def test_tc06_complete_checkout(driver):
    print("\n========== TC06: COMPLETE CHECKOUT ==========")

    inventory = do_login(driver)

    # Add product
    inventory.add_product_by_name("sauce-labs-backpack")
    pause()

    assert inventory.get_cart_count() == 1, (
        "Product was not added successfully."
    )

    # Open cart
    cart = open_cart(driver)

    items = cart.get_item_names()

    assert "Sauce Labs Backpack" in items, (
        "Backpack is missing from the cart."
    )

    print("Cart verified:", items)

    # Checkout
    cart.proceed_to_checkout()

    wait_for_url(driver, "checkout-step-one.html")
    pause()

    # Fill customer details
    checkout_one = CheckoutStepOnePage(driver)

    checkout_one.fill_form(
        "Varshith",
        "Vasamsetti",
        "533001"
    )

    pause()

    checkout_one.continue_checkout()

    wait_for_url(driver, "checkout-step-two.html")
    pause()

    # Verify order overview
    checkout_two = CheckoutStepTwoPage(driver)

    total = checkout_two.get_total()

    print("Order total:", total)

    assert "$" in total, (
        f"Order total was not displayed correctly: {total}"
    )

    # Place the test order on SauceDemo
    checkout_two.finish_order()

    wait_for_url(driver, "checkout-complete.html")
    pause(2)

    # Verify order confirmation
    confirmation = OrderConfirmationPage(driver)

    header = confirmation.get_confirmation_header()
    message = confirmation.get_confirmation_text()

    print("Confirmation header:", header)
    print("Confirmation message:", message)

    assert "thank you" in header.lower(), (
        f"Order confirmation failed: {header}"
    )

    assert message.strip(), (
        "Order confirmation message is empty."
    )

    print("TC06 PASSED - Test order completed successfully")


# ==========================================================
# TC07 - CHECKOUT FORM VALIDATION
# ==========================================================

def test_tc07_checkout_form_validation(driver):
    print("\n========== TC07: CHECKOUT FORM VALIDATION ==========")

    inventory = do_login(driver)

    inventory.add_product_by_name("sauce-labs-backpack")
    pause()

    cart = open_cart(driver)

    assert len(cart.get_item_names()) == 1, (
        "Expected one product in the cart."
    )

    cart.proceed_to_checkout()

    wait_for_url(driver, "checkout-step-one.html")
    pause()

    checkout_one = CheckoutStepOnePage(driver)

    # Submit empty form
    checkout_one.continue_checkout()
    pause()

    error = checkout_one.get_error()

    print("Empty form error:", error)

    assert "first name is required" in error.lower(), (
        f"Unexpected empty-form error: {error}"
    )

    # Enter first name only
    checkout_one.type_text(
        *CheckoutStepOnePage.FIRST_NAME,
        "Varshith"
    )

    checkout_one.continue_checkout()
    pause()

    error = checkout_one.get_error()

    print("Missing last name error:", error)

    assert "last name is required" in error.lower(), (
        f"Unexpected last-name error: {error}"
    )

    # Complete all required fields
    checkout_one.fill_form(
        "Varshith",
        "Vasamsetti",
        "533001"
    )

    checkout_one.continue_checkout()

    wait_for_url(driver, "checkout-step-two.html")
    pause()

    checkout_two = CheckoutStepTwoPage(driver)
    total = checkout_two.get_total()

    assert "$" in total, (
        "Checkout overview did not display the total."
    )

    print("TC07 PASSED")


# ==========================================================
# TC08 - LOGOUT
# ==========================================================

def test_tc08_logout(driver):
    print("\n========== TC08: LOGOUT ==========")

    inventory = do_login(driver)

    title = inventory.get_page_title()

    assert title == "Products", (
        f"Expected Products page, got: {title}"
    )

    # Open menu and log out
    inventory.logout()
    pause()

    # Verify login page is displayed
    login_page = LoginPage(driver)

    WebDriverWait(driver, WAIT_TIME).until(
        EC.visibility_of_element_located(
            LoginPage.LOGIN_BUTTON
        )
    )

    assert login_page.is_visible(*LoginPage.LOGIN_BUTTON), (
        "Login button was not visible after logout."
    )

    assert "saucedemo.com" in driver.current_url.lower(), (
        "Unexpected URL after logout."
    )

    print("TC08 PASSED")


# ==========================================================
# END OF TEST FILE
# ==========================================================