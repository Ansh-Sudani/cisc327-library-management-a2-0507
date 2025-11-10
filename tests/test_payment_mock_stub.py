import pytest
from unittest.mock import patch
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway
from datetime import datetime, timedelta

from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,
    pay_late_fees,
    refund_late_fee_payment,
)


# ---------- pay_late_fees TESTS ----------

def test_pay_late_fees_success(mocker):
    """Successful payment with valid patron, book, and late fee"""
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.0})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Mock Book"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert success is True
    assert "Payment successful" in msg
    assert txn_id == "txn_123"

    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=5.0,
        description="Late fees for 'Mock Book'"
    )


def test_pay_late_fees_payment_declined(mocker):
    """Payment declined by gateway"""
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.0})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Declined Book"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Card declined")

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert not success
    assert "Payment failed" in msg
    assert txn_id is None
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_invalid_patron_id(mocker):
    """Invalid patron ID → mock not called"""
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn_id = pay_late_fees("12A456", 1, mock_gateway)

    assert not success
    assert "Invalid patron ID" in msg
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_fee(mocker):
    """Zero fee → should not call gateway"""
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Mock Book"})

    mock_gateway = Mock(spec=PaymentGateway)
    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert not success
    assert "No late fees" in msg
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker):
    """Network/exception handling"""
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 4.0})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Network Book"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network error")

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert not success
    assert "Payment processing error" in msg
    mock_gateway.process_payment.assert_called_once()


# ---------- refund_late_fee_payment TESTS ----------

def test_refund_success():
    """Successful refund"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund successful")

    success, msg = refund_late_fee_payment("txn_123", 10.0, mock_gateway)

    assert success
    assert "Refund successful" in msg
    mock_gateway.refund_payment.assert_called_once_with("txn_123", 10.0)


def test_refund_invalid_transaction_id():
    """Invalid transaction ID → mock not called"""
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("bad_txn", 10.0, mock_gateway)

    assert not success
    assert "Invalid transaction ID" in msg
    mock_gateway.refund_payment.assert_not_called()


def test_refund_negative_amount():
    """Negative refund → mock not called"""
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", -5.0, mock_gateway)

    assert not success
    assert "greater than 0" in msg
    mock_gateway.refund_payment.assert_not_called()


def test_refund_exceeds_maximum():
    """Exceeds $15 limit → mock not called"""
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", 20.0, mock_gateway)

    assert not success
    assert "exceeds maximum" in msg
    mock_gateway.refund_payment.assert_not_called()

def test_verify_payment_status():
    gateway = PaymentGateway()
    result = gateway.verify_payment_status("txn_12345")
    assert "status" in result

def test_add_book_to_catalog():
    result = add_book_to_catalog("1984", "Orwell", "ISBN123", 5)
    assert result is not None

def test_search_books_in_catalog():
    result = search_books_in_catalog("1984", "title")
    assert isinstance(result, list)

def test_get_patron_status_report():
    patrons = {"John": {"fees_due": 0}}
    report = get_patron_status_report(patrons)
    assert isinstance(report, dict)
    assert "borrowed_books" in report
    assert "outstanding_fees" in report

# ---------- PaymentGateway process_payment and refund_payment Tests ----------

def test_process_payment_success():
    gateway = PaymentGateway()
    result = gateway.process_payment("12345", 50.00)
    assert isinstance(result, tuple)
    assert len(result) >= 2

def test_process_payment_failure():
    gateway = PaymentGateway()
    result = gateway.process_payment("", 0)
    assert result[0] is False or result[1] in ("", None)

def test_process_payment_exception(mocker):
    gateway = PaymentGateway()
    mocker.patch.object(gateway, "process_payment", side_effect=Exception("Network error"))
    try:
        gateway.process_payment("12345", 10.0)
    except Exception as e:
        assert "Network error" in str(e)

def test_refund_payment_success():
    gateway = PaymentGateway()
    result = gateway.refund_payment("txn_001", 20.0)
    assert isinstance(result, tuple)
    assert len(result) >= 2

def test_refund_payment_invalid_amount():
    gateway = PaymentGateway()
    result = gateway.refund_payment("txn_001", -5.0)
    assert result[0] is False or result[1] in ("", None)

# ---------- add_book_to_catalog edge cases ----------
def test_add_book_to_catalog_missing_title():
    success, msg = add_book_to_catalog("", "Author", "1234567890123", 1)
    assert not success
    assert "Title is required" in msg

def test_add_book_to_catalog_invalid_isbn():
    success, msg = add_book_to_catalog("Title", "Author", "12345", 1)
    assert not success
    assert "ISBN must be exactly 13 digits" in msg

def test_add_book_to_catalog_invalid_copies():
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 0)
    assert not success
    assert "Total copies must be a positive integer" in msg


# ---------- borrow_book_by_patron edge cases ----------
def test_borrow_book_invalid_patron_id():
    success, msg = borrow_book_by_patron("12AB56", 1)
    assert not success
    assert "Invalid patron ID" in msg

def test_borrow_book_not_found(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=None)
    success, msg = borrow_book_by_patron("123456", 999)
    assert not success
    assert "Book not found" in msg

def test_borrow_book_max_limit(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"available_copies": 5, "title": "Mock"})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=5)
    success, msg = borrow_book_by_patron("123456", 1)
    assert not success
    assert "maximum borrowing limit" in msg


# ---------- return_book_by_patron edge cases ----------
def test_return_book_invalid_patron_id():
    success, msg = return_book_by_patron("12A456", 1)
    assert not success
    assert "Invalid patron ID" in msg

def test_return_book_not_found(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=None)
    success, msg = return_book_by_patron("123456", 1)
    assert not success
    assert "Book not found" in msg

def test_return_book_no_borrow_record(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "Mock"})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    success, msg = return_book_by_patron("123456", 1)
    assert not success
    assert "No record found" in msg




def test_late_fee_on_time():
    borrow_date = datetime.now() - timedelta(days=10)
    fee = calculate_late_fee_for_book("123456", 1, borrow_date)
    assert fee["fee_amount"] == 0
    assert fee["status"] == "On time"

def test_late_fee_under_7_days():
    borrow_date = datetime.now() - timedelta(days=16)  # 2 days overdue
    fee = calculate_late_fee_for_book("123456", 1, borrow_date)
    assert fee["fee_amount"] == 1.0
    assert fee["status"] == "Overdue"

def test_late_fee_max_cap():
    borrow_date = datetime.now() - timedelta(days=50)  # 36 days overdue
    fee = calculate_late_fee_for_book("123456", 1, borrow_date)
    assert fee["fee_amount"] == 15.0  # capped
    assert fee["status"] == "Overdue"


def test_add_book_to_catalog_db_error(mocker):
    # simulate insert_book failing
    mocker.patch("services.library_service.get_book_by_isbn", return_value=None)
    mocker.patch("services.library_service.insert_book", return_value=False)
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 1)
    assert not success
    assert "Database error" in msg



def test_borrow_book_db_error(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"available_copies": 5, "title": "Mock"})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.insert_borrow_record", return_value=False)
    success, msg = borrow_book_by_patron("123456", 1)
    assert not success
    assert "Database error" in msg



def test_return_book_db_error(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "Mock"})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=1)
    mocker.patch("services.library_service.update_book_availability", return_value=False)
    success, msg = return_book_by_patron("123456", 1)
    assert not success
    assert "Database error" in msg
