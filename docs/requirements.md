# Requirements

| Field | Value |
|-------|-------|
| Workflow ID | `WF-EPMCDMETST-71369-20261116` |
| Jira issue key | `EPMCDMETST-71369` |
| Author role | Requirements Agent |
| Date | 2026-11-16 |
| Status | Approved |

## 1. Summary

A user of the Personal Expense Tracker must be able to record personal expenses (amount, category, description, expense date), view them most recent first, update and delete them (delete after confirmation), and filter by category and/or date range with the ability to clear filters. Input must be validated and failures must not corrupt data or leak sensitive information.

## 2. Scope

### In scope
- Create, view, update, delete and filter expenses.
- Validation, confirmation, and graceful error handling for these operations.

### Out of scope
- User registration/authentication, bank integration, automatic expense detection, payment processing, currency conversion, budget recommendations/analytics.

## 3. Functional Requirements

Acceptance criteria are numbered AC-001..AC-016 in the order listed in section 5 of `docs/user-story.md`. User answers (2026-11-16) are cited as Q-numbers from section 7.

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| REQ-001 | The system shall allow the user to create a new expense. | Must | AC-001 |
| REQ-002 | Each created expense shall include amount, category, description and expense date. | Must | AC-002 |
| REQ-003 | The system shall validate mandatory fields on create. Amount, category, description and expense date are all mandatory. If any is missing, no expense is created and a meaningful validation message is shown for each missing field. | Must | AC-003, Q1 |
| REQ-004 | The system shall validate that the amount is a numeric value greater than zero on create and update; an invalid amount prevents creation/update and shows a message that the amount must be greater than zero. | Must | AC-004 |
| REQ-005 | On successful creation, the system shall display a confirmation. | Must | AC-005 |
| REQ-006 | The system shall allow the user to view all recorded expenses. | Must | AC-006 |
| REQ-007 | The expense list shall display amount, category, description and expense date for each expense. The amount is shown without a currency symbol. | Must | AC-007, Q2 |
| REQ-008 | The expense list shall be ordered by expense date, most recent first (descending). | Must | AC-008, Q4 |
| REQ-009 | When no expenses exist, the system shall display a no-expenses message. | Must | AC-009 |
| REQ-010 | The system shall allow the user to select an existing expense and update its details; updated values shall be validated (per REQ-003, REQ-004, REQ-021, REQ-022, REQ-023) and, once saved, reflected in the expense list. Invalid updates shall not be saved and shall show meaningful validation messages. | Must | AC-010, AC-004, AC-003 |
| REQ-011 | The system shall delete an existing expense only after asking the user for confirmation; on confirm the expense is removed from the list; on cancel the expense is not deleted and remains listed. | Must | AC-011 |
| REQ-012 | The system shall allow filtering expenses by category, chosen from the predefined category list, showing only matching expenses. | Must | AC-012 |
| REQ-013 | The system shall allow filtering expenses by a date range (start and end date), showing only expenses whose expense date is within the range. Both bounds are inclusive. Either bound may be omitted (an omitted bound leaves that side of the range open). | Must | AC-012, Q5 |
| REQ-014 | When a category and a date range are both applied, the system shall show only expenses matching both. | Must | AC-012 |
| REQ-015 | The system shall allow the user to clear applied filters and return to viewing all expenses. | Must | AC-013 |
| REQ-016 | Each expense shall have a unique identifier. The identifier is not shown to the user. | Must | AC-014, Q10 |
| REQ-017 | The system shall restrict update and delete to existing expenses; an attempt on a non-existent expense shall modify no records and be handled gracefully with a non-sensitive message. | Must | AC-015 |
| REQ-018 | The category of an expense shall be selected from a fixed predefined list: Food, Transport, Housing, Utilities, Entertainment, Health, Shopping, Other. The list is not user-editable. | Must | AC-012, AC-002 (story section 2), Q3 |
| REQ-019 | The system shall display meaningful validation messages for invalid input. | Must | AC-016 |
| REQ-020 | On unexpected errors, the system shall not create or leave inconsistent or corrupted expense records. | Must | AC-016 |
| REQ-021 | The amount shall have at most 2 decimal places and shall not exceed 999,999.99; values above the maximum or with more than 2 decimal places are rejected with a meaningful message (create and update). | Must | AC-004, Q2 |
| REQ-022 | The expense date shall use the format YYYY-MM-DD and shall not be in the future; future or incorrectly formatted dates are rejected with a meaningful message (create and update). | Must | AC-003, AC-016, Q6/Q7 |
| REQ-023 | The description shall be at most 200 characters; longer values are rejected with a meaningful message (create and update). | Must | AC-003, AC-016, Q6/Q7 |
| REQ-024 | If the date range start is after the end, the system shall show a validation message and not apply the invalid range. | Must | AC-012, Q5 |
| REQ-025 | When a filter (category, date range, or both) matches no expenses, the system shall display a "no expenses match the filters" message, distinct from the no-expenses message of REQ-009. | Must | AC-012, AC-009, Q6/Q7 |
| REQ-026 | On successful update and on successful delete, the system shall display a success message. | Should | Q10 (extends AC-005 pattern) |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Source |
|----|----------|-------------|--------|
| REQ-NFR-001 | Security | Error messages and logs shall not expose sensitive information, defined as stack traces, file paths and other internal details. Messages shall be generic. | AC-016, AC-015, Q8 |
| REQ-NFR-002 | Data integrity | A failed or invalid create/update/delete operation shall leave existing expense records unchanged. | AC-016, AC-015 |
| REQ-NFR-003 | Usability | Validation and error messages shall be meaningful, identifying the field and the problem. | AC-003, AC-004, AC-016 |
| REQ-NFR-004 | Quality (Definition of Done) | Unit tests shall cover core business logic; integration tests shall cover important workflows. | Definition of Done in story |

No volume, performance, availability or accessibility targets are required beyond basic usability (Q9). The platform/interface is left to the Architecture stage (Q11); no interface constraint is set here.

## 5. Assumptions

| # | Assumption | Impact if wrong |
|---|------------|-----------------|
| 1 | Expenses persist between uses of the application (the story does not say so explicitly). | If not required, persistence requirements and tests change. |
| 2 | The application serves a single user's data set; there is no per-user separation because authentication is out of scope. | Multi-user data separation would be a new requirement. |
| 3 | Update and delete outcomes warrant user feedback (now confirmed by Q10, see REQ-026; kept as assumption for the story's silence). | Minor; extra messages may be unnecessary. |
| 4 | Ordering of expenses sharing the same expense date is not specified by the user (Q4). Assumed that the order must still be deterministic (repeated views of unchanged data show the same order); the specific tie-break rule is left to Architecture. | If wrong, list order could vary between views and tests of ordering could be flaky. |
| 5 | "Future" in REQ-022 is relative to the current date at the time of submission. Time zone handling is not specified. | Dates near midnight could be accepted or rejected unexpectedly. |
| 6 | Description length (200) counts characters, and whitespace-only text counts as missing for REQ-003. | A whitespace-only description could be accepted if not treated as missing. |

## 6. Constraints and Dependencies

- Work is limited to the listed functions; out-of-scope items must not be added.
- Categories are the fixed list in REQ-018.
- Definition of Done (story): all ACs implemented, unit and integration tests, code review findings addressed or documented, application verification, documentation updated.

## 7. Open Questions

All questions from round 1 were answered by the user on 2026-11-16 and are resolved. No blocking questions remain.

| # | Question (short) | Resolution (user answer) | Status |
|---|------------------|--------------------------|--------|
| 1 | Mandatory fields | All four mandatory (REQ-003) | Resolved |
| 2 | Amount constraints | 2 decimals, max 999,999.99, no currency symbol (REQ-007, REQ-021) | Resolved |
| 3 | Categories | Fixed default list, not user-editable (REQ-018) | Resolved |
| 4 | Ordering | Expense date descending; tie order unspecified (REQ-008, Assumption 4) | Resolved |
| 5 | Date range | Inclusive, bounds optional, start after end shows validation message (REQ-013, REQ-024) | Resolved |
| 6 | Filter with no matches | Distinct message (REQ-025) | Resolved |
| 7 | Date and description rules | No future dates, YYYY-MM-DD, description max 200 (REQ-022, REQ-023) | Resolved |
| 8 | Sensitive information | No stack traces, file paths or internals; generic errors (REQ-NFR-001) | Resolved |
| 9 | Volume/performance/accessibility | No targets beyond basic usability | Resolved |
| 10 | Update/delete messages; ID visibility | Success messages on update and delete; ID hidden (REQ-026, REQ-016) | Resolved |
| 11 | Platform/interface | Left to Architecture | Resolved |

## 8. Traceability

| Acceptance Criterion | Requirement(s) |
|----------------------|----------------|
| AC-001 | REQ-001 |
| AC-002 | REQ-002, REQ-018 |
| AC-003 | REQ-003, REQ-010, REQ-022, REQ-023, REQ-NFR-003 |
| AC-004 | REQ-004, REQ-010, REQ-021, REQ-NFR-003 |
| AC-005 | REQ-005, REQ-026 |
| AC-006 | REQ-006 |
| AC-007 | REQ-007 |
| AC-008 | REQ-008 |
| AC-009 | REQ-009, REQ-025 |
| AC-010 | REQ-010 |
| AC-011 | REQ-011, REQ-026 |
| AC-012 | REQ-012, REQ-013, REQ-014, REQ-018, REQ-024, REQ-025 |
| AC-013 | REQ-015 |
| AC-014 | REQ-016 |
| AC-015 | REQ-017, REQ-NFR-001, REQ-NFR-002 |
| AC-016 | REQ-019, REQ-020, REQ-022, REQ-023, REQ-NFR-001, REQ-NFR-002, REQ-NFR-003 |
| Definition of Done | REQ-NFR-004 |

## 8.1 Amendment: Change Requests (2026-11-17)

Two user-requested change requests. They add no new user-story acceptance criteria and trace to the user's request of 2026-11-17, not to the Jira story. Existing REQ and AC text above is unchanged. Per the user's choice "Short amendment, no gate reopen (Recommended)", G1 is not reopened; the Orchestrator records this in `docs/workflow-state.md`. Status of these items: Accepted by user choice "Short amendment, no gate reopen (Recommended)" on 2026-11-17, recorded by the Orchestrator.

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| REQ-CR-001 | The application shall present a clean, minimal visual style: a neutral colour palette, a readable expense list, clearly identifiable buttons, visibly distinguished error and validation messages, and a layout that remains usable on narrow (mobile) and wide screens. The styling shall be delivered with no new dependencies and no client-side scripting. | Should | User request 2026-11-17 (CR-001): "Clean and minimal (Recommended)" |
| REQ-CR-002 | Date entry (the expense date on create and update, and the filter start and end dates) shall offer a native browser calendar picker. Server-side date validation (REQ-022, REQ-024) shall be unchanged. A minimal accent colour shall be used in the visual style. | Should | User request 2026-11-17 (CR-002): "while choosing date we should be able to choose from calender a minimal calender should open it will be more convenient for user and also add some coloring not too much just minimal" |

### Acceptance statements (testable)

REQ-CR-001
- The stylesheet is served successfully and is linked on every page, including error pages (for example not-found and unexpected-error pages).
- Pages render with the stylesheet applied: buttons, list and messages are visually distinguishable from plain text; error/validation messages are visually distinct from success messages.
- The layout has no horizontal scrolling at a narrow viewport width (about 360 px) and remains readable at a wide desktop width.
- No new dependency is added and no JavaScript is required for the styling.
- All existing behaviour (REQ-001..REQ-026) and its tests are unaffected.

REQ-CR-002
- The expense date field on create and update, and the filter start and end date fields, are date inputs (HTML `type="date"`) that open the browser's native calendar picker.
- A hand-posted request with an invalid, incorrectly formatted or future date still produces the existing validation error and creates/updates nothing (REQ-022).
- A hand-posted filter with start after end still shows the existing validation message (REQ-024).
- A valid previously entered date is retained on redisplay. A value that is not a valid ISO date is dropped by the browser's date control (known limitation, FND-023, accepted; see ADR 0005).
- The accent colour is limited to a minimal set of elements (for example primary buttons, links, focus/heading accents); the overall palette stays neutral.

### Traceability (amendment)

| Source | Requirement(s) |
|--------|----------------|
| User request 2026-11-17 (CR-001) | REQ-CR-001 |
| User request 2026-11-17 (CR-002) | REQ-CR-002 (relates to REQ-022, REQ-024, which remain unchanged) |

### Assumptions (amendment)

| # | Assumption | Impact if wrong |
|---|------------|-----------------|
| CR-A1 | Both items are priority Should (presentation only, no change to story behaviour). | If the user wants Must, they become release-blocking. |
| CR-A2 | Native picker appearance and locale are controlled by the browser and are not specified. Browsers without date-input support fall back to text entry validated server-side. | Appearance may differ between browsers; this is accepted. |
| CR-A3 | No specific accent colour is mandated; the colour choice (teal was used in implementation) is left to implementation. | A mandated colour would need to be stated. |

No open questions.

## 9. Approval

Gate G1 approval is recorded by the Orchestrator in `docs/workflow-state.md`.

| Gate | Status | Approver | Date |
|------|--------|----------|------|
| G1 | Approved | User (Sagar Chaudhary) | 2026-11-16 |
