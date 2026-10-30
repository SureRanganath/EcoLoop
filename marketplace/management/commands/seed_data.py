"""
Management command to seed EcoLoop with demonstration data.
Safe to rerun — skips existing records by username.

Demo credentials (LOCAL DEVELOPMENT ONLY):
  Suppliers: supplier1 / supplier2 / supplier3  password: EcoLoop@123
  Buyers:    buyer1 / buyer2 / buyer3            password: EcoLoop@123
  Admin:     admin                               password: EcoLoop@123
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from marketplace.models import MaterialCategory, WasteListing, PurchaseRequest
from accounts.models import UserProfile
import random

CATEGORIES = [
    ('Plastic', 'bi-recycle', 'primary'),
    ('Metal', 'bi-tools', 'secondary'),
    ('Paper & Cardboard', 'bi-file-earmark', 'warning'),
    ('Glass', 'bi-gem', 'info'),
    ('Textile', 'bi-scissors', 'danger'),
    ('Rubber', 'bi-circle', 'dark'),
    ('Organic By-products', 'bi-tree', 'success'),
    ('Other Industrial', 'bi-gear', 'secondary'),
]

SUPPLIERS = [
    ('supplier1', 'Ravi', 'Kumar', 'supplier1@ecoloop.dev', 'Greentech Plastics Pvt Ltd', 'Plastics Manufacturing', 'Hyderabad', 'Telangana'),
    ('supplier2', 'Priya', 'Sharma', 'supplier2@ecoloop.dev', 'MetalWorks India', 'Metal Fabrication', 'Pune', 'Maharashtra'),
    ('supplier3', 'Arjun', 'Reddy', 'supplier3@ecoloop.dev', 'PaperCycle Industries', 'Paper Manufacturing', 'Chennai', 'Tamil Nadu'),
    ('supplier4', 'Sunita', 'Patel', 'supplier4@ecoloop.dev', 'Gujarat Glass Works', 'Glass Manufacturing', 'Ahmedabad', 'Gujarat'),
    ('supplier5', 'Mohan', 'Das', 'supplier5@ecoloop.dev', 'Textile Surplus Co', 'Textile Manufacturing', 'Surat', 'Gujarat'),
]

BUYERS = [
    ('buyer1', 'Anita', 'Singh', 'buyer1@ecoloop.dev', 'EcoPlast Recyclers', 'Plastic Recycling', 'Hyderabad', 'Telangana'),
    ('buyer2', 'Vikram', 'Nair', 'buyer2@ecoloop.dev', 'GreenMetal Solutions', 'Metal Recycling', 'Mumbai', 'Maharashtra'),
    ('buyer3', 'Deepa', 'Iyer', 'buyer3@ecoloop.dev', 'PaperMill Recyclers', 'Paper Recycling', 'Bengaluru', 'Karnataka'),
    ('buyer4', 'Rahul', 'Gupta', 'buyer4@ecoloop.dev', 'CircularGlass Ltd', 'Glass Recycling', 'Delhi', 'Delhi'),
    ('buyer5', 'Kavya', 'Menon', 'buyer5@ecoloop.dev', 'FabricLoop Pvt Ltd', 'Textile Recycling', 'Kochi', 'Kerala'),
]

LISTINGS_DATA = [
    ('Recycled HDPE Plastic Pellets', 'Plastic', 'High-density polyethylene pellets from post-industrial waste. Suitable for pipe and container manufacturing.', 500, 45, 'A', 'Hyderabad', 'Telangana'),
    ('PET Plastic Scraps', 'Plastic', 'Clean PET plastic scraps from bottle manufacturing. Ideal for fibre and packaging applications.', 300, 35, 'B', 'Pune', 'Maharashtra'),
    ('PVC Pipe Offcuts', 'Plastic', 'PVC pipe offcuts from construction projects. Can be reprocessed into new PVC products.', 200, 20, 'C', 'Chennai', 'Tamil Nadu'),
    ('Polypropylene Film Waste', 'Plastic', 'Polypropylene film waste from food packaging. Clean and sorted.', 150, 30, 'B', 'Ahmedabad', 'Gujarat'),
    ('Steel Scrap Grade A', 'Metal', 'Heavy melting steel scrap from manufacturing. High iron content, low impurities.', 1000, 28, 'A', 'Pune', 'Maharashtra'),
    ('Aluminium Offcuts', 'Metal', 'Aluminium sheet offcuts from aerospace component manufacturing. 6061 alloy.', 250, 85, 'A', 'Bengaluru', 'Karnataka'),
    ('Copper Wire Scrap', 'Metal', 'Bare bright copper wire scrap from electrical installations. 99% purity.', 100, 450, 'A', 'Mumbai', 'Maharashtra'),
    ('Cast Iron Turnings', 'Metal', 'Cast iron turnings from machine shop operations. Suitable for foundry use.', 800, 12, 'C', 'Coimbatore', 'Tamil Nadu'),
    ('Corrugated Cardboard Waste', 'Paper & Cardboard', 'Clean corrugated cardboard from warehouse operations. Baled and ready for recycling.', 2000, 5, 'B', 'Delhi', 'Delhi'),
    ('Office Paper Waste', 'Paper & Cardboard', 'Sorted office paper waste. White and coloured paper separated. Suitable for pulp production.', 500, 8, 'A', 'Hyderabad', 'Telangana'),
    ('Newspaper Waste', 'Paper & Cardboard', 'Bulk newspaper waste from distribution centres. Suitable for newsprint recycling.', 1500, 4, 'C', 'Kolkata', 'West Bengal'),
    ('Flat Glass Cullet', 'Glass', 'Flat glass cullet from window manufacturing. Clear glass, sorted by colour.', 600, 6, 'B', 'Ahmedabad', 'Gujarat'),
    ('Glass Bottle Cullet', 'Glass', 'Mixed colour glass bottle cullet from beverage industry. Crushed and sorted.', 400, 4, 'C', 'Nashik', 'Maharashtra'),
    ('Cotton Fabric Offcuts', 'Textile', 'Cotton fabric offcuts from garment manufacturing. Various colours and sizes.', 300, 15, 'B', 'Surat', 'Gujarat'),
    ('Polyester Yarn Waste', 'Textile', 'Polyester yarn waste from textile mills. Suitable for recycled fibre production.', 200, 22, 'B', 'Tirupur', 'Tamil Nadu'),
    ('Natural Rubber Crumb', 'Rubber', 'Natural rubber crumb from tyre retreading. Suitable for playground surfaces and mats.', 400, 18, 'B', 'Kochi', 'Kerala'),
    ('EPDM Rubber Offcuts', 'Rubber', 'EPDM rubber offcuts from automotive sealing strip production.', 150, 25, 'A', 'Chennai', 'Tamil Nadu'),
    ('Rice Husk Biomass', 'Organic By-products', 'Rice husk from rice milling operations. Suitable for biomass energy and silica extraction.', 5000, 2, 'B', 'Patna', 'Bihar'),
    ('Spent Coffee Grounds', 'Organic By-products', 'Spent coffee grounds from instant coffee manufacturing. Suitable for composting and biogas.', 800, 3, 'C', 'Bengaluru', 'Karnataka'),
    ('Industrial Solvent Waste', 'Other Industrial', 'Mixed industrial solvent waste from paint manufacturing. Requires proper handling. Suitable for solvent recovery.', 200, 8, 'D', 'Vadodara', 'Gujarat'),
    ('Printed Circuit Board Scrap', 'Other Industrial', 'PCB scrap from electronics manufacturing. Contains recoverable precious metals.', 50, 120, 'B', 'Noida', 'Uttar Pradesh'),
    ('Polystyrene Foam Waste', 'Plastic', 'Expanded polystyrene foam waste from packaging. Compacted for transport.', 100, 12, 'C', 'Jaipur', 'Rajasthan'),
    ('Brass Turnings', 'Metal', 'Brass turnings from precision machining. High copper content.', 180, 320, 'A', 'Rajkot', 'Gujarat'),
    ('Kraft Paper Waste', 'Paper & Cardboard', 'Kraft paper waste from packaging operations. Suitable for recycled kraft production.', 700, 6, 'B', 'Hyderabad', 'Telangana'),
]


class Command(BaseCommand):
    help = 'Seed EcoLoop with demonstration data (safe to rerun)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')
        cat_map = {}
        for name, icon, color in CATEGORIES:
            cat, _ = MaterialCategory.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name), 'icon': icon, 'color': color}
            )
            cat_map[name] = cat

        self.stdout.write('Seeding supplier accounts...')
        supplier_users = []
        for username, first, last, email, company, industry, city, state in SUPPLIERS:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='EcoLoop@123',
                                                 first_name=first, last_name=last, email=email)
                UserProfile.objects.create(user=user, role='supplier', company_name=company,
                                           industry_type=industry, city=city, state=state, is_verified=True)
            supplier_users.append(User.objects.get(username=username))

        self.stdout.write('Seeding buyer accounts...')
        for username, first, last, email, company, industry, city, state in BUYERS:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='EcoLoop@123',
                                                 first_name=first, last_name=last, email=email)
                UserProfile.objects.create(user=user, role='buyer', company_name=company,
                                           industry_type=industry, city=city, state=state, is_verified=True)

        self.stdout.write('Seeding waste listings...')
        for i, (title, cat_name, desc, qty, price, grade, city, state) in enumerate(LISTINGS_DATA):
            if not WasteListing.objects.filter(title=title).exists():
                supplier = supplier_users[i % len(supplier_users)]
                WasteListing.objects.create(
                    supplier=supplier,
                    title=title,
                    category=cat_map[cat_name],
                    description=desc,
                    quantity=qty,
                    price_per_kg=price,
                    quality_grade=grade,
                    city=city,
                    state=state,
                    status='available',
                )

        self.stdout.write('Seeding purchase requests...')
        buyer_users = [User.objects.get(username=b[0]) for b in BUYERS]
        listings = list(WasteListing.objects.all()[:10])
        statuses = ['completed', 'completed', 'accepted', 'pending', 'rejected']
        for i, listing in enumerate(listings):
            buyer = buyer_users[i % len(buyer_users)]
            if buyer != listing.supplier and not PurchaseRequest.objects.filter(buyer=buyer, listing=listing).exists():
                PurchaseRequest.objects.create(
                    buyer=buyer,
                    listing=listing,
                    requested_quantity=min(listing.quantity * 3 / 10, listing.quantity),
                    proposed_price=listing.price_per_kg * 95 / 100,
                    message='Interested in purchasing this material for our recycling operations.',
                    status=statuses[i % len(statuses)],
                )

        # Create admin if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@ecoloop.dev', 'EcoLoop@123')
            self.stdout.write('Created admin user.')

        self.stdout.write(self.style.SUCCESS(
            '\nDemo data seeded successfully!\n'
            'Credentials (LOCAL DEV ONLY):\n'
            '  Suppliers: supplier1-5 / EcoLoop@123\n'
            '  Buyers:    buyer1-5   / EcoLoop@123\n'
            '  Admin:     admin      / EcoLoop@123\n'
        ))
