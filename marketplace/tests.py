from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from marketplace.models import MaterialCategory, WasteListing, PurchaseRequest, FavouriteListing
from decimal import Decimal


def make_supplier(username='sup1', password='TestPass@123'):
    user = User.objects.create_user(username=username, password=password,
                                     first_name='Test', last_name='Supplier', email=f'{username}@test.com')
    UserProfile.objects.create(user=user, role='supplier', company_name='Test Supplier Co',
                                industry_type='Manufacturing', city='Hyderabad', state='Telangana')
    return user


def make_buyer(username='buy1', password='TestPass@123'):
    user = User.objects.create_user(username=username, password=password,
                                     first_name='Test', last_name='Buyer', email=f'{username}@test.com')
    UserProfile.objects.create(user=user, role='buyer', company_name='Test Buyer Co',
                                industry_type='Recycling', city='Pune', state='Maharashtra')
    return user


def make_category():
    return MaterialCategory.objects.create(name='Plastic', slug='plastic', icon='bi-recycle', color='primary')


def make_listing(supplier, category, qty=500, price=45):
    return WasteListing.objects.create(
        supplier=supplier, title='Test Plastic Scraps', category=category,
        description='High quality plastic scraps for recycling',
        quantity=Decimal(str(qty)), price_per_kg=Decimal(str(price)),
        quality_grade='A', city='Hyderabad', state='Telangana', status='available'
    )


# ── Authentication Tests ──────────────────────────────────────────────────────

class RegistrationTest(TestCase):
    def test_register_supplier(self):
        response = self.client.post(reverse('register'), {
            'username': 'newsup', 'first_name': 'New', 'last_name': 'Supplier',
            'email': 'newsup@test.com', 'password1': 'TestPass@123', 'password2': 'TestPass@123',
            'role': 'supplier', 'company_name': 'New Co', 'industry_type': 'Mfg',
            'city': 'Delhi', 'state': 'Delhi',
        })
        self.assertEqual(User.objects.filter(username='newsup').count(), 1)
        self.assertEqual(UserProfile.objects.get(user__username='newsup').role, 'supplier')

    def test_register_buyer(self):
        self.client.post(reverse('register'), {
            'username': 'newbuy', 'first_name': 'New', 'last_name': 'Buyer',
            'email': 'newbuy@test.com', 'password1': 'TestPass@123', 'password2': 'TestPass@123',
            'role': 'buyer', 'company_name': 'Buy Co', 'industry_type': 'Recycling',
            'city': 'Mumbai', 'state': 'Maharashtra',
        })
        self.assertEqual(UserProfile.objects.get(user__username='newbuy').role, 'buyer')

    def test_duplicate_username_rejected(self):
        make_supplier('dup1')
        response = self.client.post(reverse('register'), {
            'username': 'dup1', 'first_name': 'A', 'last_name': 'B',
            'email': 'dup@test.com', 'password1': 'TestPass@123', 'password2': 'TestPass@123',
            'role': 'buyer', 'company_name': 'Co', 'industry_type': 'X',
            'city': 'X', 'state': 'Delhi',
        })
        self.assertEqual(User.objects.filter(username='dup1').count(), 1)

    def test_login_valid(self):
        make_supplier('loginsup')
        response = self.client.post(reverse('login'), {'username': 'loginsup', 'password': 'TestPass@123'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {'username': 'nobody', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        make_supplier('outsup')
        self.client.login(username='outsup', password='TestPass@123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))


# ── Role Permission Tests ─────────────────────────────────────────────────────

class RolePermissionTest(TestCase):
    def setUp(self):
        self.supplier = make_supplier()
        self.buyer = make_buyer()
        self.category = make_category()

    def test_buyer_cannot_add_listing(self):
        self.client.login(username='buy1', password='TestPass@123')
        response = self.client.post(reverse('add_listing'), {
            'title': 'Hack', 'category': self.category.pk, 'description': 'x',
            'quantity': 100, 'price_per_kg': 10, 'quality_grade': 'A',
            'city': 'X', 'state': 'Delhi', 'status': 'available',
        })
        self.assertEqual(WasteListing.objects.count(), 0)

    def test_supplier_cannot_submit_request(self):
        listing = make_listing(self.supplier, self.category)
        self.client.login(username='sup1', password='TestPass@123')
        response = self.client.post(reverse('submit_request', args=[listing.pk]), {
            'requested_quantity': 100, 'message': 'test',
        })
        self.assertEqual(PurchaseRequest.objects.count(), 0)

    def test_unauthenticated_redirected_from_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_supplier_cannot_edit_others_listing(self):
        sup2 = make_supplier('sup2')
        listing = make_listing(self.supplier, self.category)
        self.client.login(username='sup2', password='TestPass@123')
        response = self.client.post(reverse('edit_listing', args=[listing.pk]), {
            'title': 'Hacked', 'category': self.category.pk, 'description': 'x',
            'quantity': 100, 'price_per_kg': 10, 'quality_grade': 'A',
            'city': 'X', 'state': 'Delhi', 'status': 'available',
        })
        listing.refresh_from_db()
        self.assertEqual(listing.title, 'Test Plastic Scraps')


# ── Listing CRUD Tests ────────────────────────────────────────────────────────

class ListingCRUDTest(TestCase):
    def setUp(self):
        self.supplier = make_supplier()
        self.category = make_category()
        self.client.login(username='sup1', password='TestPass@123')

    def test_create_listing(self):
        response = self.client.post(reverse('add_listing'), {
            'title': 'New Plastic', 'category': self.category.pk,
            'description': 'Good quality plastic scraps',
            'quantity': '200', 'price_per_kg': '30', 'quality_grade': 'B',
            'city': 'Hyderabad', 'state': 'Telangana', 'status': 'available',
        })
        self.assertEqual(WasteListing.objects.filter(title='New Plastic').count(), 1)

    def test_negative_quantity_rejected(self):
        self.client.post(reverse('add_listing'), {
            'title': 'Bad', 'category': self.category.pk, 'description': 'x',
            'quantity': '-10', 'price_per_kg': '10', 'quality_grade': 'A',
            'city': 'X', 'state': 'Delhi', 'status': 'available',
        })
        self.assertEqual(WasteListing.objects.count(), 0)

    def test_negative_price_rejected(self):
        self.client.post(reverse('add_listing'), {
            'title': 'Bad2', 'category': self.category.pk, 'description': 'x',
            'quantity': '100', 'price_per_kg': '-5', 'quality_grade': 'A',
            'city': 'X', 'state': 'Delhi', 'status': 'available',
        })
        self.assertEqual(WasteListing.objects.count(), 0)

    def test_edit_listing(self):
        listing = make_listing(self.supplier, self.category)
        self.client.post(reverse('edit_listing', args=[listing.pk]), {
            'title': 'Updated Title', 'category': self.category.pk,
            'description': 'Updated desc', 'quantity': '300', 'price_per_kg': '50',
            'quality_grade': 'A', 'city': 'Hyderabad', 'state': 'Telangana', 'status': 'available',
        })
        listing.refresh_from_db()
        self.assertEqual(listing.title, 'Updated Title')

    def test_delete_listing(self):
        listing = make_listing(self.supplier, self.category)
        self.client.post(reverse('delete_listing', args=[listing.pk]))
        self.assertEqual(WasteListing.objects.count(), 0)


# ── Marketplace Search & Filter Tests ────────────────────────────────────────

class MarketplaceFilterTest(TestCase):
    def setUp(self):
        self.supplier = make_supplier()
        self.category = make_category()
        make_listing(self.supplier, self.category, qty=500, price=45)
        cat2 = MaterialCategory.objects.create(name='Metal', slug='metal', icon='bi-tools', color='secondary')
        WasteListing.objects.create(
            supplier=self.supplier, title='Steel Scrap', category=cat2,
            description='Heavy steel scrap', quantity=Decimal('1000'),
            price_per_kg=Decimal('28'), quality_grade='A',
            city='Pune', state='Maharashtra', status='available'
        )

    def test_search_by_name(self):
        response = self.client.get(reverse('marketplace'), {'q': 'plastic'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plastic Scraps')
        self.assertNotContains(response, 'Steel Scrap')

    def test_filter_by_category(self):
        response = self.client.get(reverse('marketplace'), {'category': 'metal'})
        self.assertContains(response, 'Steel Scrap')
        self.assertNotContains(response, 'Test Plastic Scraps')

    def test_filter_by_state(self):
        response = self.client.get(reverse('marketplace'), {'state': 'Maharashtra'})
        self.assertContains(response, 'Steel Scrap')
        self.assertNotContains(response, 'Test Plastic Scraps')

    def test_filter_by_min_qty(self):
        response = self.client.get(reverse('marketplace'), {'min_qty': '600'})
        self.assertContains(response, 'Steel Scrap')
        self.assertNotContains(response, 'Test Plastic Scraps')

    def test_filter_by_max_price(self):
        response = self.client.get(reverse('marketplace'), {'max_price': '30'})
        self.assertContains(response, 'Steel Scrap')
        self.assertNotContains(response, 'Test Plastic Scraps')


# ── Purchase Request Tests ────────────────────────────────────────────────────

class PurchaseRequestTest(TestCase):
    def setUp(self):
        self.supplier = make_supplier()
        self.buyer = make_buyer()
        self.category = make_category()
        self.listing = make_listing(self.supplier, self.category, qty=500)

    def test_buyer_can_submit_request(self):
        self.client.login(username='buy1', password='TestPass@123')
        self.client.post(reverse('submit_request', args=[self.listing.pk]), {
            'requested_quantity': '100', 'message': 'Interested',
        })
        self.assertEqual(PurchaseRequest.objects.count(), 1)

    def test_quantity_exceeding_available_rejected(self):
        self.client.login(username='buy1', password='TestPass@123')
        self.client.post(reverse('submit_request', args=[self.listing.pk]), {
            'requested_quantity': '9999', 'message': 'Too much',
        })
        self.assertEqual(PurchaseRequest.objects.count(), 0)

    def test_supplier_can_accept_request(self):
        pr = PurchaseRequest.objects.create(
            buyer=self.buyer, listing=self.listing,
            requested_quantity=Decimal('100'), status='pending'
        )
        self.client.login(username='sup1', password='TestPass@123')
        self.client.post(reverse('update_request_status', args=[pr.pk]), {'status': 'accepted'})
        pr.refresh_from_db()
        self.assertEqual(pr.status, 'accepted')

    def test_supplier_can_reject_request(self):
        pr = PurchaseRequest.objects.create(
            buyer=self.buyer, listing=self.listing,
            requested_quantity=Decimal('100'), status='pending'
        )
        self.client.login(username='sup1', password='TestPass@123')
        self.client.post(reverse('update_request_status', args=[pr.pk]), {'status': 'rejected'})
        pr.refresh_from_db()
        self.assertEqual(pr.status, 'rejected')

    def test_buyer_can_cancel_pending_request(self):
        pr = PurchaseRequest.objects.create(
            buyer=self.buyer, listing=self.listing,
            requested_quantity=Decimal('100'), status='pending'
        )
        self.client.login(username='buy1', password='TestPass@123')
        self.client.post(reverse('cancel_request', args=[pr.pk]))
        pr.refresh_from_db()
        self.assertEqual(pr.status, 'cancelled')

    def test_buyer_cannot_update_request_status(self):
        pr = PurchaseRequest.objects.create(
            buyer=self.buyer, listing=self.listing,
            requested_quantity=Decimal('100'), status='pending'
        )
        self.client.login(username='buy1', password='TestPass@123')
        self.client.post(reverse('update_request_status', args=[pr.pk]), {'status': 'accepted'})
        pr.refresh_from_db()
        self.assertEqual(pr.status, 'pending')


# ── Favourite Tests ───────────────────────────────────────────────────────────

class FavouriteTest(TestCase):
    def setUp(self):
        self.supplier = make_supplier()
        self.buyer = make_buyer()
        self.category = make_category()
        self.listing = make_listing(self.supplier, self.category)

    def test_add_favourite(self):
        self.client.login(username='buy1', password='TestPass@123')
        self.client.get(reverse('toggle_favourite', args=[self.listing.pk]))
        self.assertEqual(FavouriteListing.objects.filter(user=self.buyer, listing=self.listing).count(), 1)

    def test_remove_favourite(self):
        FavouriteListing.objects.create(user=self.buyer, listing=self.listing)
        self.client.login(username='buy1', password='TestPass@123')
        self.client.get(reverse('toggle_favourite', args=[self.listing.pk]))
        self.assertEqual(FavouriteListing.objects.filter(user=self.buyer, listing=self.listing).count(), 0)

    def test_no_duplicate_favourites(self):
        self.client.login(username='buy1', password='TestPass@123')
        self.client.get(reverse('toggle_favourite', args=[self.listing.pk]))
        self.client.get(reverse('toggle_favourite', args=[self.listing.pk]))
        self.client.get(reverse('toggle_favourite', args=[self.listing.pk]))
        self.assertLessEqual(FavouriteListing.objects.filter(user=self.buyer, listing=self.listing).count(), 1)


# ── Recommendation Engine Tests ───────────────────────────────────────────────

class RecommendationTest(TestCase):
    def setUp(self):
        self.supplier = make_supplier()
        self.category = make_category()
        self.listing = make_listing(self.supplier, self.category, qty=500, price=45)

    def test_recommendations_returned(self):
        from ml.recommender import get_recommendations
        results = get_recommendations(
            query_text='plastic scraps recycling',
            category_id=self.category.pk,
            requested_qty=200,
            max_budget=50,
            preferred_state='Telangana',
            listings=WasteListing.objects.all(),
        )
        self.assertGreater(len(results), 0)

    def test_score_between_0_and_100(self):
        from ml.recommender import get_recommendations
        results = get_recommendations(
            query_text='plastic',
            category_id=None,
            requested_qty=100,
            max_budget=None,
            preferred_state=None,
            listings=WasteListing.objects.all(),
        )
        for r in results:
            self.assertGreaterEqual(r['score'], 0)
            self.assertLessEqual(r['score'], 100)

    def test_unavailable_listings_excluded(self):
        from ml.recommender import get_recommendations
        self.listing.status = 'sold'
        self.listing.save()
        results = get_recommendations(
            query_text='plastic',
            category_id=None,
            requested_qty=100,
            max_budget=None,
            preferred_state=None,
            listings=WasteListing.objects.all(),
        )
        self.assertEqual(len(results), 0)

    def test_quantity_score_full_when_sufficient(self):
        from ml.recommender import score_quantity
        self.assertEqual(score_quantity(100, 500), 1.0)

    def test_quantity_score_partial_when_insufficient(self):
        from ml.recommender import score_quantity
        score = score_quantity(500, 100)
        self.assertLess(score, 1.0)
        self.assertGreater(score, 0.0)

    def test_price_score_full_within_budget(self):
        from ml.recommender import score_price
        self.assertEqual(score_price(50, 45), 1.0)

    def test_price_score_reduced_over_budget(self):
        from ml.recommender import score_price
        self.assertLess(score_price(30, 60), 1.0)

    def test_location_score_same_state(self):
        from ml.recommender import score_location
        self.assertEqual(score_location('Telangana', 'Telangana'), 1.0)

    def test_location_score_different_state(self):
        from ml.recommender import score_location
        self.assertLess(score_location('Telangana', 'Maharashtra'), 1.0)

    def test_category_suggestion(self):
        from ml.recommender import suggest_category
        label, confidence = suggest_category('plastic scraps PET HDPE polymer')
        self.assertEqual(label, 'Plastic')
        self.assertGreater(confidence, 0)


# ── Analytics Tests ───────────────────────────────────────────────────────────

class AnalyticsTest(TestCase):
    def setUp(self):
        self.supplier = make_supplier()
        self.buyer = make_buyer()
        self.category = make_category()
        self.listing = make_listing(self.supplier, self.category)
        PurchaseRequest.objects.create(
            buyer=self.buyer, listing=self.listing,
            requested_quantity=Decimal('100'), status='completed'
        )
        self.client.login(username='sup1', password='TestPass@123')

    def test_analytics_page_loads(self):
        response = self.client.get(reverse('analytics'))
        self.assertEqual(response.status_code, 200)

    def test_analytics_counts_from_db(self):
        response = self.client.get(reverse('analytics'))
        self.assertEqual(response.context['total_listings'], 1)
        self.assertEqual(response.context['completed_exchanges'], 1)

    def test_exchanged_qty_calculated(self):
        response = self.client.get(reverse('analytics'))
        self.assertEqual(float(response.context['exchanged_qty']), 100.0)
