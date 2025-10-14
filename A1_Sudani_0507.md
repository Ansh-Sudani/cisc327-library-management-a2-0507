# Assignment 1 - Project Implementation Status

**Name:** Ansh Sudani  
**Student ID:** 20410507
**Group Number:** 4

| Function Name                  | Requirement | Implementation Status | What is Missing / Notes |
|--------------------------------|------------|--------------------|------------------------|
| add_book_to_catalog             | R1         | Complete           | Fully implemented with input validation and duplicate ISBN check. |
| Catalog display (route + template)| R2         | Complete           | Implemented in `catalog_routes.py` and `catalog.html`; no separate business logic function. |
| borrow_book_by_patron           | R3         | Partial            | Borrowing works, but patron limit check incorrectly uses `>` instead of `>= 5`. |
| return_book_by_patron           | R4         | Not Implemented    | Function returns placeholder; does not update book availability, record return date, or calculate late fees. |
| calculate_late_fee_for_book     | R5         | Not Implemented    | Placeholder only; logic for overdue days and fee calculation not implemented. |
| search_books_in_catalog         | R6         | Not Implemented    | Placeholder only; does not search books by title, author, or ISBN. |
| get_patron_status_report        | R7         | Not Implemented    | Placeholder only; does not provide borrowed books, due dates, fees, or borrowing history. |
