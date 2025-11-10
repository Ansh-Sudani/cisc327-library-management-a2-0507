import pytest
from services.library_service import get_patron_status_report

def test_status_report_full():
    report = get_patron_status_report("123456")
    
    # Check the report structure
    assert isinstance(report, dict)
    assert "patron_id" in report
    assert report["patron_id"] == "123456"
    
    # Check currently borrowed books
    assert "borrowed_books" in report
    assert isinstance(report["borrowed_books"], list)
    assert "total_borrowed" in report
    assert report["total_borrowed"] == len(report["borrowed_books"])
    
    # Check outstanding fees
    assert "outstanding_fees" in report
    assert isinstance(report["outstanding_fees"], (int, float))
    
    # Check borrowing history
    assert "borrowing_history" in report
    assert isinstance(report["borrowing_history"], list)

