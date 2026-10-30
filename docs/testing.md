# Testing Report — EcoLoop

## Test Execution

Framework: Django TestCase (unittest)
Command: `python manage.py test marketplace --verbosity=2`
Django version: 6.1.2
Python version: 3.14.3
Result: **42 tests — ALL PASSED**
Duration: ~68 seconds

## Test Results by Category

### Registration & Authentication (6 tests) — PASS
- test_register_supplier — supplier account created with correct role
- test_register_buyer — buyer account created with correct role
- test_duplicate_username_rejected — duplicate username blocked
- test_login_valid — valid credentials redirect to dashboard
- test_login_invalid — invalid credentials stay on login page
- test_logout — logout redirects to home

### Role-Based Permissions (4 tests) — PASS
- test_buyer_cannot_add_listing — buyer POST to add_listing creates no listing
- test_supplier_cannot_submit_request — supplier POST to submit_request creates no request
- test_unauthenticated_redirected_from_dashboard — unauthenticated GET redirects to login
- test_supplier_cannot_edit_others_listing — supplier cannot modify another supplier's listing

### Listing CRUD & Validation (5 tests) — PASS
- test_create_listing — supplier can create a valid listing
- test_negative_quantity_rejected — quantity <= 0 rejected by form
- test_negative_price_rejected — negative price rejected by form
- test_edit_listing — supplier can update their own listing
- test_delete_listing — supplier can delete their own listing

### Marketplace Search & Filters (5 tests) — PASS
- test_search_by_name — text search returns matching listings only
- test_filter_by_category — category filter returns correct listings
- test_filter_by_state — state filter returns correct listings
- test_filter_by_min_qty — minimum quantity filter works correctly
- test_filter_by_max_price — maximum price filter works correctly

### Purchase Request Workflow (6 tests) — PASS
- test_buyer_can_submit_request — buyer can submit a valid request
- test_quantity_exceeding_available_rejected — over-quantity request blocked
- test_supplier_can_accept_request — supplier can accept pending request
- test_supplier_can_reject_request — supplier can reject pending request
- test_buyer_can_cancel_pending_request — buyer can cancel their pending request
- test_buyer_cannot_update_request_status — buyer cannot accept/reject requests

### Favourite Listings (3 tests) — PASS
- test_add_favourite — toggle adds favourite
- test_remove_favourite — second toggle removes favourite
- test_no_duplicate_favourites — no duplicate favourites created

### Recommendation Engine (9 tests) — PASS
- test_recommendations_returned — engine returns results for valid query
- test_score_between_0_and_100 — all scores in valid range
- test_unavailable_listings_excluded — sold listings not recommended
- test_quantity_score_full_when_sufficient — score_quantity returns 1.0 when sufficient
- test_quantity_score_partial_when_insufficient — score_quantity < 1.0 when insufficient
- test_price_score_full_within_budget — score_price returns 1.0 within budget
- test_price_score_reduced_over_budget — score_price < 1.0 over budget
- test_location_score_same_state — score_location returns 1.0 for same state
- test_location_score_different_state — score_location < 1.0 for different state

### Category Suggestion (1 test) — PASS
- test_category_suggestion — classifier correctly predicts 'Plastic' for plastic description

### Analytics (3 tests) — PASS
- test_analytics_page_loads — analytics view returns HTTP 200
- test_analytics_counts_from_db — total_listings and completed_exchanges match DB
- test_exchanged_qty_calculated — exchanged_qty correctly sums completed request quantities

## Notes

- Tests use Django's in-memory SQLite test database — no production data is affected.
- All tests are independent and can be run in any order.
- The category classifier test uses the small built-in training dataset in ml/recommender.py.
