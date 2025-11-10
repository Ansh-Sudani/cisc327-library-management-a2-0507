import unittest
from services.library_service import get_patron_status_report

class TestGetPatronStatusReport(unittest.TestCase):

    def test_status_report_contains_expected_fields(self):
        patron_id = "123456"
        report = get_patron_status_report(patron_id)

        self.assertEqual(report["patron_id"], patron_id)
        self.assertIn("borrowed_books", report)
        self.assertIn("borrowing_history", report)
        self.assertIn("total_borrowed", report)
        self.assertIn("outstanding_fees", report)
        self.assertIsInstance(report["borrowed_books"], list)
        self.assertIsInstance(report["borrowing_history"], list)
        self.assertIsInstance(report["total_borrowed"], int)
        self.assertIsInstance(report["outstanding_fees"], float)

    def test_status_report_mocked_data(self):
        report = get_patron_status_report("123456")
        self.assertEqual(report["total_borrowed"], len(report["borrowed_books"]))
        # Due dates and statuses should be present
        for book in report["borrowed_books"]:
            self.assertIn("title", book)
            self.assertIn("due_date", book)
            self.assertIn("status", book)

if __name__ == '__main__':
    unittest.main()