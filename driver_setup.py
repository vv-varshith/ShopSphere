# ============================================================
#  SauceDemo Automation - Browser Driver Setup
#  Tester: Varshith Vasamsetti
#  Fix: Using Selenium built-in manager (no webdriver-manager)
# ============================================================

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import subprocess
import sys
import os
import config


def get_driver():
    """Initialize and return WebDriver using Selenium built-in manager."""
    if config.BROWSER.lower() == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        # Suppress Chrome internal error logs (GCM, updater, etc.)
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--no-first-run")
        # Selenium 4.6+ built-in driver manager
        driver = webdriver.Chrome(options=options)

    elif config.BROWSER.lower() == "firefox":
        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()

    else:
        raise ValueError(f"Unsupported browser: {config.BROWSER}")

    driver.implicitly_wait(config.IMPLICIT_WAIT)
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    return driver
