# EcoLoop — Circular Economy Marketplace for Industrial Waste Exchange

A final-year Computer Science Engineering major project.

## Quick Start (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open http://127.0.0.1:8000

## Demo Credentials (LOCAL DEV ONLY)

| Role     | Username       | Password     |
|----------|----------------|--------------|
| Supplier | supplier1–5    | EcoLoop@123  |
| Buyer    | buyer1–5       | EcoLoop@123  |
| Admin    | admin          | EcoLoop@123  |

Admin panel: http://127.0.0.1:8000/admin

## Run Tests

```
python manage.py test marketplace --verbosity=2
```

## Project Structure

```
EcoLoop/
├── config/          Django project settings and URLs
├── accounts/        User registration, login, profiles, dashboards
├── marketplace/     Listings, purchase requests, favourites, contact
├── recommendations/ AI recommendation engine and category suggester
├── analytics/       Platform statistics and Chart.js dashboards
├── core/            Home, about, error pages
├── ml/              recommender.py — TF-IDF + multi-factor scoring
├── templates/       All HTML templates
├── static/          CSS, JS, images
├── media/           Uploaded files
├── docs/            Project documentation
└── requirements.txt
```

## Technology Stack

- Python 3.14 / Django 6.1
- SQLite database
- Bootstrap 5 + Bootstrap Icons
- scikit-learn (TF-IDF, cosine similarity, Logistic Regression)
- pandas, NumPy
- Chart.js (analytics charts)
- python-dotenv

## Features

- Supplier and Buyer role-based accounts
- Waste material listings with search, filter, sort, pagination
- AI recommendation engine with explainable scores
- AI category suggestion (TF-IDF + Logistic Regression)
- Purchase request workflow (submit → accept/reject → complete)
- Favourite listings
- Transaction history
- Interactive analytics dashboard (5 Chart.js charts)
- Django Admin for platform management
- 42 automated tests — all passing
