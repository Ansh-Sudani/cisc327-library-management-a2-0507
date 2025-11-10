import pytest
from datetime import datetime, timedelta
from services.library_service import calculate_late_fee_for_book

# ----------------------------
# Test: On-time or not overdue
# ----------------------------
def test_fee_zero_on_time():
    borrow_date = datetime.now() - timedelta(days=10)  # borrowed 10 days ago
    return_date = borrow_date + timedelta(days=14)     # returned exactly on due date
    result = calculate_late_fee_for_book("123456", 1, borrow_date, return_date)
    assert isinstance(result, dict)
    assert result["fee_amount"] == 0.0
    assert result["days_overdue"] == 0
    assert result["status"].lower() == "on time"

# ----------------------------
# Test: Overdue <= 7 days
# ----------------------------
def test_fee_first_seven_days():
    borrow_date = datetime.now() - timedelta(days=16)  # borrowed 16 days ago
    return_date = borrow_date + timedelta(days=15)     # 1 day overdue
    result = calculate_late_fee_for_book("123456", 1, borrow_date, return_date)
    assert result["days_overdue"] == 1
    assert result["fee_amount"] == 0.5
    assert result["status"].lower() == "overdue"

# ----------------------------
# Test: Overdue > 7 days
# ----------------------------
def test_fee_after_seven_days():
    borrow_date = datetime.now() - timedelta(days=25)  # borrowed 25 days ago
    return_date = borrow_date + timedelta(days=25)     # 11 days overdue
    result = calculate_late_fee_for_book("123456", 1, borrow_date, return_date)
    expected_fee = (0.5 * 7) + (1.0 * 4)  # first 7 days + next 4 days
    assert result["days_overdue"] == 11
    assert result["fee_amount"] == expected_fee
    assert result["status"].lower() == "overdue"

# ----------------------------
# Test: Maximum fee capped at $15
# ----------------------------
def test_fee_max_cap():
    borrow_date = datetime.now() - timedelta(days=50)  # borrowed 50 days ago
    return_date = borrow_date + timedelta(days=50)     # 36 days overdue
    result = calculate_late_fee_for_book("123456", 1, borrow_date, return_date)
    assert result["fee_amount"] == 15.0
    assert result["days_overdue"] > 7
    assert result["status"].lower() == "overdue"
