# SauceDemo Automation Framework
### Tester: **Varshith Vasamsetti**
### Website: https://www.saucedemo.com/

---

## 📌 Project Overview

This is a **Selenium + Pytest** automation framework for the SauceDemo online store.  
It covers **8 end-to-end test cases** including login, sorting, cart operations, checkout validation, and logout.

---

## 🗂️ Project Structure

```
ShopSphere/
├── config.py              → Configuration (URL, credentials, browser settings)
├── driver_setup.py        → WebDriver initialization (Chrome/Firefox)
├── pages.py               → Page Object Models for all pages
├── conftest.py            → Pytest fixtures, screenshot on failure, HTML report setup
├── test_saucedemo.py      → 8 Test Cases (main test file)
├── run_tests.bat          → One-click script to install & run all tests
├── requirements.txt       → Python dependencies
├── reports/               → Auto-generated HTML reports
└── screenshots/           → Auto-saved on test failure
```

---

## ✅ 8 Test Cases

| # | Test Case | Description |
|---|-----------|-------------|
| TC01 | Valid Login | Login with correct credentials → Products page |
| TC02 | Invalid Login | Login with wrong password → Error message |
| TC03 | Product Sorting | Sort A→Z, Z→A, Price Low→High, Price High→Low |
| TC04 | Add to Cart | Add 2 products → Verify cart badge count |
| TC05 | Remove from Cart | Add product, navigate to cart, remove it |
| TC06 | End-to-End Checkout | Full order: Login → Add → Cart → Checkout → Confirm |
| TC07 | Form Validation | Submit empty form → check required field errors |
| TC08 | Logout | Click logout → Verify redirect to Login page |

---

## ⚙️ Prerequisites

- **Python 3.8+** installed
- **Google Chrome** browser installed
- Internet connection (ChromeDriver auto-downloaded)

---

## 🚀 How to Run

### Option 1: One-Click (Windows)
```
Double-click: run_tests.bat
```

### Option 2: Manual (Command Prompt / PowerShell)

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Run all 8 tests with HTML report
pytest test_saucedemo.py -v -s --html=reports/saucedemo_report.html --self-contained-html

# Step 3: Run a specific test case
pytest test_saucedemo.py::test_tc06_complete_checkout -v -s
```

---

## 📊 Output After Running

- **Console** → Step-by-step logs with ✅ PASSED / ❌ FAILED status
- **HTML Report** → `reports/saucedemo_report.html` (open in browser)
- **Screenshots** → `screenshots/` folder (auto-captured only on failures)

---

## 🔑 Test Credentials

| Field | Value |
|-------|-------|
| Username | `standard_user` |
| Password | `secret_sauce` |
| Tester | Varshith Vasamsetti |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Programming language |
| Selenium 4 | Browser automation |
| Pytest | Test framework |
| pytest-html | HTML report generation |
| webdriver-manager | Auto ChromeDriver download |
| Page Object Model | Design pattern for maintainability |

---

## 📝 Notes

- The browser window opens automatically, runs tests step by step, waits 1 second between steps, then **closes automatically**.
- If a test **fails**, a screenshot is saved in the `screenshots/` folder automatically.
- To switch to Firefox, change `BROWSER = "firefox"` in `config.py`.
