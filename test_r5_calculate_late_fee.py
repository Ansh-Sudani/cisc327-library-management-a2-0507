import unittest
from datetime import datetime, timedelta
from services.library_service import calculate_late_fee_for_book

class TestCalculateLateFeeForBook(unittest.TestCase):

    def setUp(self):
        self.patron_id = "123456"
        self.book_id = 1
        self.borrow_date = datetime(2025, 1, 1)

    def test_on_time_return_exactly_due_date(self):
        return_date = self.borrow_date + timedelta(days=14)
        result = calculate_late_fee_for_book(self.patron_id, self.book_id, self.borrow_date, return_date)
        self.assertEqual(result['fee_amount'], 0.0)
        self.assertEqual(result['days_overdue'], 0)
        self.assertEqual(result['status'], 'On time')

    def test_return_before_due_date(self):
        return_date = self.borrow_date + timedelta(days=10)
        result = calculate_late_fee_for_book(self.patron_id, self.book_id, self.borrow_date, return_date)
        self.assertEqual(result['fee_amount'], 0.0)
        self.assertEqual(result['days_overdue'], 0)
        self.assertEqual(result['status'], 'On time')

    def test_return_5_days_late(self):
        return_date = self.borrow_date + timedelta(days=19)  # 5 days overdue
        result = calculate_late_fee_for_book(self.patron_id, self.book_id, self.borrow_date, return_date)
        self.assertEqual(result['days_overdue'], 5)
        self.assertAlmostEqual(result['fee_amount'], 2.5)
        self.assertEqual(result['status'], 'Overdue')

    def test_return_7_days_late(self):
        return_date = self.borrow_date + timedelta(days=21)  # 7 days overdue
        result = calculate_late_fee_for_book(self.patron_id, self.book_id, self.borrow_date, return_date)
        self.assertEqual(result['days_overdue'], 7)
        self.assertAlmostEqual(result['fee_amount'], 3.5)
        self.assertEqual(result['status'], 'Overdue')

    def test_return_10_days_late(self):
        return_date = self.borrow_date + timedelta(days=24)  # 10 days overdue
        result = calculate_late_fee_for_book(self.patron_id, self.book_id, self.borrow_date, return_date)
        self.assertEqual(result['days_overdue'], 10)
        # 7*0.5 + 3*1.0 = 3.5 + 3 = 6.5
        self.assertAlmostEqual(result['fee_amount'], 6.5)
        self.assertEqual(result['status'], 'Overdue')

    def test_return_50_days_late_capped_fee(self):
        return_date = self.borrow_date + timedelta(days=64)  # 50 days overdue
        result = calculate_late_fee_for_book(self.patron_id, self.book_id, self.borrow_date, return_date)
        self.assertEqual(result['days_overdue'], 50)
        self.assertEqual(result['fee_amount'], 15.00)
        self.assertEqual(result['status'], 'Overdue')

if __name__ == '__main__':
    unittest.main()