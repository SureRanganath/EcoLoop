# System Architecture — EcoLoop

## Overview

EcoLoop follows Django's MVT (Model-View-Template) architecture with a separate ML module.

## Request Flow

```
HTTP Request
    │
    ▼
Django URL Router (config/urls.py)
    │
    ▼
View Function (accounts/marketplace/recommendations/analytics/core)
    │
    ├── Django ORM → SQLite Database
    │
    ├── ml/recommender.py (for AI views)
    │       └── scikit-learn TF-IDF + scoring
    │
    ▼
Template (Bootstrap 5 HTML)
    │
    ▼
HTTP Response
```

## App Responsibilities

```
config/          Project settings, root URL conf, WSGI
accounts/        UserProfile model, registration, login, dashboards, profile
marketplace/     MaterialCategory, WasteListing, PurchaseRequest,
                 FavouriteListing, ContactMessage models + views + forms
recommendations/ Recommendation and category suggestion views
analytics/       Analytics view — aggregates DB stats for Chart.js
core/            Home, about, error handlers
ml/              recommender.py — pure Python AI logic (no Django dependency)
templates/       All Jinja-compatible Django templates
static/          main.css
media/           User-uploaded images
docs/            Project documentation
```

## Database Schema (simplified)

```
auth_user ──────────────────────────────────────────────────────┐
    │                                                            │
    ▼                                                            │
accounts_userprofile (role, company, city, state, ...)          │
                                                                 │
marketplace_materialcategory (name, slug, icon, color)          │
    │                                                            │
    ▼                                                            │
marketplace_wastelisting (supplier→User, category→Category,     │
    title, description, quantity, price_per_kg, quality_grade,  │
    city, state, image, status, created_at, updated_at)         │
    │                                                            │
    ├──────────────────────────────────────────────────────────┐ │
    ▼                                                          ▼ ▼
marketplace_purchaserequest (buyer→User, listing→Listing,   marketplace_favouritelisting
    requested_quantity, proposed_price, message, status)     (user→User, listing→Listing)

marketplace_contactmessage (name, email, subject, message, is_read)
```

## AI Module Architecture

```
ml/recommender.py
├── build_text_corpus(listings)       → list of combined text strings
├── compute_text_similarity(q, corpus) → numpy array of cosine similarities
├── score_quantity(requested, available) → float 0–1
├── score_price(budget, price)           → float 0–1
├── score_location(preferred, listing)   → float 0–1
├── get_recommendations(...)             → list of scored dicts
├── get_category_classifier()            → sklearn Pipeline
└── suggest_category(text)              → (label, confidence%)
```

## Security

- CSRF protection on all POST forms (Django middleware)
- Password hashing via Django's PBKDF2 hasher
- Login required decorators on all authenticated views
- Server-side role checks (supplier/buyer) before write operations
- Owner checks before edit/delete operations
- Form validation on both client and server side
- Environment-based SECRET_KEY via python-dotenv
