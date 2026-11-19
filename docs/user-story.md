# User Story

| Field | Value |
|-------|-------|
| Workflow ID | WF-EPMCDMETST-71369-20261116 |
| Jira key | EPMCDMETST-71369 |
| Author role | Orchestrator (intake, read-only from Jira) |
| Date | 2026-11-16 |
| Status | Draft |
| Jira type / status / priority | Story / Open / Average |

> Source: Jira, treated as untrusted text. Reproduced without changes in meaning.

## Title
Add and manage personal expenses

## 1. Summary
Add and manage personal expenses to track spending.

## 2. General description
As a user,
I want to record and manage my personal expenses (add, view, update, delete, and filter),
So that I can track where my money is being spent and monitor my spending habits.

The Personal Expense Tracker application must allow users to:
- Add daily expenses with **amount, category, description, and expense date**.
- View all recorded expenses including these fields, ordered with the most recent first.
- Update or delete an existing expense when necessary.
- Filter expenses by **category** and by a **date range**, and clear filters to return to the full list.

Validation and error handling must ensure mandatory fields are provided, the amount is a positive numeric value (> 0), and invalid operations do not result in corrupted or inconsistent expense records. Expense categories must be selected from a predefined list. Each expense must have a unique identifier.

Out of scope: user registration/authentication, bank integration, automatic expense detection, payment processing, currency conversion, budget recommendations/analytics.

## 3. Preconditions
- The Personal Expense Tracker application is available to the user.
- The user has access to the expense management feature (add/view/update/delete/filter) within the application.

## 4. Scenarios of use
1. **Add a new expense successfully**: Given the user is on the expense entry form, when they enter an amount > 0, select a category from the predefined list, enter a description and select an expense date, and submit, then the system creates a new expense with a unique identifier and displays a confirmation.
2. **Fail to add an expense with missing mandatory fields**: When the user submits with one or more mandatory fields empty, then no expense is created and meaningful validation messages are shown for each missing field.
3. **Fail to add an expense with a non-positive amount**: When the amount is not > 0 and the user submits, then no expense is created and a message says the amount must be greater than zero.
4. **View expenses when expenses exist**: On navigating to the list, all recorded expenses are shown with amount, category, description and expense date, most recent first.
5. **View expenses when none exist**: The system displays a message that no expenses exist.
6. **Update an existing expense successfully**: Viewing the list, the user selects an expense, updates one or more fields with valid values and saves; the expense is updated and reflected in the list.
7. **Fail to update with invalid values**: With missing mandatory fields or amount not > 0, changes are not saved and meaningful validation messages are shown.
8. **Delete an expense after confirmation**: On selecting delete, the system asks for confirmation; on confirm, the expense is deleted and no longer listed.
9. **Cancel expense deletion**: On cancel, the expense is not deleted and remains listed.
10. **Filter by category**: Only expenses matching the selected category are shown.
11. **Filter by date range**: With a start and end date, only expenses with dates within the range are shown.
12. **Filter by category and date range together**: Only expenses matching both are shown.
13. **Clear filters**: All recorded expenses are shown again.
14. **Update or delete a non-existent expense**: No records are modified and the error is handled gracefully without exposing sensitive information.

## 5. Acceptance criteria
1. The user can create a new expense.
2. Each created expense includes: expense amount, category, description, and expense date.
3. Mandatory fields are validated; if any are missing, the expense is not created and meaningful validation messages are shown.
4. The expense amount is validated as a positive numeric value greater than zero; invalid amounts prevent creation/update and show a meaningful message.
5. On successful expense creation, the system displays a confirmation.
6. The user can view all previously recorded expenses.
7. The expense list displays amount, category, description, and expense date for each expense.
8. The expense list is ordered with the most recent expense first.
9. When no expenses exist, the system displays an appropriate no-expenses message.
10. The user can select an existing expense and update its details; updated values are validated and are reflected in the expense list after saving.
11. The user can delete an existing expense only after the system asks for confirmation; after deletion the expense no longer appears in the expense list.
12. The user can filter expenses by category (from the predefined list) and by a date range; the system shows only matching expenses.
13. The user can clear applied filters and return to viewing all expenses.
14. Each expense has a unique identifier.
15. An expense must exist before it can be updated or deleted; attempts to update/delete a non-existent expense do not modify records and are handled gracefully.
16. The application displays meaningful validation messages for invalid input and handles unexpected errors without corrupting or creating inconsistent expense records and without exposing sensitive information in error messages or logs.

## Definition of Done (provided)
All acceptance criteria implemented; unit tests cover core business logic; integration tests cover important workflows; code review findings addressed or documented; application verification completed; implementation/testing documentation updated.
