# ============================================================
#  SauceDemo Automation - conftest.py
#  Tester  : Varshith Vasamsetti
#  Features: Auto screenshots, Excel report, Desktop notify,
#            Retry on fail, Clean logs
# ============================================================

import pytest
import os
import time
import json
from datetime import datetime
from driver_setup import get_driver

# ── Excel report (openpyxl) ──────────────────────────────
try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# ── Windows Desktop Notification (win10toast) ────────────
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False

# ── TC order map ─────────────────────────────────────────
TC_ORDER = {
    "test_tc01_valid_login"              : "TC01",
    "test_tc02_invalid_login"            : "TC02",
    "test_tc03_product_sorting"          : "TC03",
    "test_tc04_add_to_cart"              : "TC04",
    "test_tc05_remove_from_cart"         : "TC05",
    "test_tc06_complete_checkout"        : "TC06",
    "test_tc07_checkout_form_validation" : "TC07",
    "test_tc08_logout"                   : "TC08",
}

# Shared results store for Excel report
_results = []


# ─────────────────────────────────────────────────────────
#  Driver fixture – fresh browser per test
# ─────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def driver():
    drv = get_driver()
    yield drv
    time.sleep(1.5)
    drv.quit()


# ─────────────────────────────────────────────────────────
#  Hook – screenshot + result capture after every test
# ─────────────────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome  = yield
    rep      = outcome.get_result()
    driver   = item.funcargs.get("driver", None)

    if rep.when == "call":
        tc_num    = TC_ORDER.get(item.name, item.name)
        status    = "PASS" if rep.passed else "FAIL"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        duration  = f"{rep.duration:.2f}s"

        # ── Screenshot ──────────────────────────────────
        screenshot_path = ""
        if driver:
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = f"screenshots/{tc_num}_{status}_{timestamp}.png"
            try:
                driver.save_screenshot(screenshot_path)
                print(f"\n📸 Screenshot: {screenshot_path}")
            except Exception:
                pass

        # ── Collect result for Excel ─────────────────────
        _results.append({
            "tc_num"    : tc_num,
            "name"      : item.name,
            "status"    : status,
            "duration"  : duration,
            "timestamp" : timestamp,
            "screenshot": screenshot_path,
            "error"     : str(rep.longrepr) if rep.failed else "",
        })


# ─────────────────────────────────────────────────────────
#  Hook – after all tests: Excel report + notification
# ─────────────────────────────────────────────────────────
def pytest_sessionfinish(session, exitstatus):
    passed = sum(1 for r in _results if r["status"] == "PASS")
    failed = sum(1 for r in _results if r["status"] == "FAIL")
    total  = len(_results)

    # ── Excel Report ─────────────────────────────────────
    if EXCEL_AVAILABLE and _results:
        _generate_excel_report(passed, failed, total)

    # ── Desktop Notification ─────────────────────────────
    _send_notification(passed, failed, total)

    # ── Summary Print ────────────────────────────────────
    print("\n")
    print("=" * 60)
    print("   📊 SAUCEDEMO AUTOMATION SUMMARY")
    print("   👤 Tester : Varshith Vasamsetti")
    print(f"   ✅ Passed : {passed}/{total}")
    print(f"   ❌ Failed : {failed}/{total}")
    print("   📄 HTML   : reports/saucedemo_report.html")
    if EXCEL_AVAILABLE:
        print("   📊 Excel  : reports/saucedemo_report.xlsx")
    print("   📸 Screenshots : screenshots/")
    print("=" * 60)


def _generate_excel_report(passed, failed, total):
    """Create a styled Excel report with test results."""
    os.makedirs("reports", exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Test Results"

    # Colour palette
    GREEN  = PatternFill("solid", fgColor="00C853")
    RED    = PatternFill("solid", fgColor="D50000")
    BLUE   = PatternFill("solid", fgColor="1565C0")
    GREY   = PatternFill("solid", fgColor="ECEFF1")
    WHITE  = Font(color="FFFFFF", bold=True)
    BLACK  = Font(color="000000", bold=True)
    CENTER = Alignment(horizontal="center", vertical="center")
    thin   = Side(style="thin")
    BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ── Title Row ────────────────────────────────────────
    ws.merge_cells("A1:F1")
    title_cell = ws["A1"]
    title_cell.value    = "SauceDemo Automation Report — Varshith Vasamsetti"
    title_cell.font     = Font(color="FFFFFF", bold=True, size=14)
    title_cell.fill     = BLUE
    title_cell.alignment = CENTER
    ws.row_dimensions[1].height = 30

    # ── Summary Row ──────────────────────────────────────
    ws.merge_cells("A2:F2")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws["A2"].value     = f"Run Date: {ts}   |   Total: {total}   |   Passed: {passed}   |   Failed: {failed}"
    ws["A2"].font      = Font(bold=True, size=11)
    ws["A2"].fill      = GREY
    ws["A2"].alignment = CENTER
    ws.row_dimensions[2].height = 22

    # ── Headers ──────────────────────────────────────────
    headers = ["TC #", "Test Name", "Status", "Duration", "Timestamp", "Screenshot"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font      = WHITE
        cell.fill      = BLUE
        cell.alignment = CENTER
        cell.border    = BORDER
    ws.row_dimensions[3].height = 18

    # ── Data Rows ────────────────────────────────────────
    for row_idx, r in enumerate(_results, start=4):
        data = [r["tc_num"], r["name"], r["status"],
                r["duration"], r["timestamp"], r["screenshot"]]
        fill = GREEN if r["status"] == "PASS" else RED
        for col_idx, val in enumerate(data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border    = BORDER
            cell.alignment = CENTER
            if col_idx == 3:          # Status column coloured
                cell.fill = fill
                cell.font = WHITE
        ws.row_dimensions[row_idx].height = 16

    # Column widths
    for col, width in zip("ABCDEF", [8, 38, 10, 12, 20, 50]):
        ws.column_dimensions[chr(64 + col)].width = width

    path = "reports/saucedemo_report.xlsx"
    wb.save(path)
    print(f"\n📊 Excel report saved: {path}")


def _send_notification(passed, failed, total):
    """Windows desktop notification after test run."""
    msg = f"✅ {passed} Passed  ❌ {failed} Failed  (Total: {total})"
    try:
        if TOAST_AVAILABLE:
            n = ToastNotifier()
            n.show_toast(
                "SauceDemo Automation Done!",
                msg,
                duration=6,
                threaded=True,
            )
        else:
            # Fallback: PowerShell balloon notification
            ps_cmd = (
                f'powershell -Command "Add-Type -AssemblyName System.Windows.Forms;'
                f'$n=[System.Windows.Forms.NotifyIcon]::new();'
                f'$n.Icon=[System.Drawing.SystemIcons]::Information;'
                f'$n.Visible=$true;'
                f'$n.ShowBalloonTip(5000,\'SauceDemo Done!\',\'{msg}\',0);'
                f'Start-Sleep 6;$n.Dispose()"'
            )
            os.system(ps_cmd)
    except Exception:
        pass  # Notification errors never block the run


# ── pytest-html customisation ─────────────────────────────
def pytest_configure(config):
    config._metadata = {}


def pytest_html_report_title(report):
    report.title = "SauceDemo Automation Report – Varshith Vasamsetti"
