# EcoLoop — Circular Economy Marketplace for Industrial Waste Exchange

> A final-year Computer Science Engineering major project: a role-based marketplace where
> industries list reusable waste materials and industries buy them as raw inputs, matched by an
> explainable AI recommendation engine.

---

## Table of contents

1. [Overview](#1-overview)
2. [Features](#2-features)
3. [Technology stack](#3-technology-stack)
4. [How to start](#4-how-to-start)
5. [Configuration](#5-configuration)
6. [How to log in (by role)](#6-how-to-log-in-by-role)
7. [What each role can do](#7-what-each-role-can-do)
8. [Project structure](#8-project-structure)
9. [Data model](#9-data-model)
10. [AI recommendation engine](#10-ai-recommendation-engine)
11. [UI and image assets](#11-ui-and-image-assets)
12. [Testing](#12-testing)
13. [Troubleshooting](#13-troubleshooting)
14. [Security notes](#14-security-notes)
15. [Known limitations and roadmap](#15-known-limitations-and-roadmap)

---

## 1. Overview

EcoLoop connects two sides of an industrial waste exchange:

- **Suppliers** publish listings for waste material they want to dispose of (quantity, price per kg,
  quality grade, location, photo).
- **Buyers** search and filter the marketplace, receive AI-ranked matches for their material
  description, save favourites, and submit purchase requests.
- **Suppliers** accept / reject / complete those requests; both sides track history and transactions.
- **Admins** manage everything through the Django admin and inspect platform-wide analytics.

The platform ships with seeded demo data so it is explorable immediately after `runserver`.

| | |
|---|---|
| Live data source | Neon Postgres (cloud), `DATABASE_URL` in `.env` |
| Local fallback | SQLite, used automatically when `DATABASE_URL` is unset |
| Test suite | **48 tests — all passing** |
| Seeded content | 14 users · 8 material categories · 24 listings · 11 purchase requests |

---

## 2. Features

**Accounts & roles**
- Supplier / Buyer registration with role selection, company details, Indian state dropdown
- Profile editing (company, industry, address, website, bio, avatar)
- Every user is guaranteed a profile (auto-created signal + backfill migration)

**Marketplace**
- Listings with search, category/state/quantity/price filters, 5 sort orders, pagination (12/page)
- Listing detail with related items, supplier info, quality grade
- Purchase request workflow: submit → accept / reject → complete, or cancel while pending
- Favourites (AJAX heart toggle) and transaction history
- Contact form with admin-visible inbox

**AI**
- Content-based recommender: TF-IDF cosine similarity + weighted scoring, with a plain-English
  explanation and per-factor bars for every result
- Category suggester: TF-IDF + Logistic Regression classifier on free-text descriptions

**Insights & UX**
- Analytics dashboard: 8 KPIs + 5 Chart.js charts (category, monthly trend, state, users, quantity)
- Category image slots, scroll-reveal animations, staggered landing transitions, animated counters
- Custom 403 / 404 / 500 pages, Django messages with auto-dismiss alerts

---

## 3. Technology stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | Django 6.1 (server-rendered templates) |
| Database | Neon Postgres via `psycopg` 3.3 (SQLite fallback locally) |
| ML / data | scikit-learn (TF-IDF, cosine similarity, Logistic Regression), pandas, NumPy |
| Frontend | Bootstrap 5.3 + Bootstrap Icons, Inter font, Chart.js 4 |
| Styling | Custom design system: `static/css/main.css` + `animations.css` |
| Behaviour | Vanilla JS: `static/js/main.js` (observers, AJAX favourites, landing transitions) |
| Config | `python-dotenv` (`.env`) |
| Images | Pillow (listing uploads + category WebP generation) |

---

## 4. How to start

### 4.1 Prerequisites

- Python 3.14 (3.12+ should work) with `pip`
- Network access to Neon (the database is cloud-hosted)

### 4.2 First-time setup

```bash
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` in the project root (copy from `.env.example`):

```
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

> **No `DATABASE_URL`?** The app falls back to local SQLite automatically — everything still works,
> just on `db.sqlite3` instead of the cloud database.

### 4.3 Run it

```bash
python manage.py migrate       # apply schema (idempotent)
python manage.py seed_data     # optional: demo data — safe to re-run, everything is guarded
python manage.py runserver
```

Open **http://127.0.0.1:8000**

### 4.4 Everyday commands

| Task | Command |
|---|---|
| Start the server | `python manage.py runserver` |
| System check | `python manage.py check` |
| Apply migrations | `python manage.py migrate` |
| Re-seed demo data (idempotent) | `python manage.py seed_data` |
| Run tests | `python manage.py test accounts marketplace --noinput` |
| Make new migrations | `python manage.py makemigrations` |
| Change an admin password | `python manage.py changepassword admin` |
| Django shell | `python manage.py shell` |
| Admin panel | http://127.0.0.1:8000/admin |

> This repository is already migrated and seeded against Neon, so on a fresh clone you normally only
> need `pip install -r requirements.txt` and `runserver`.

---

## 5. Configuration

All settings are read from `.env` by `config/settings.py`:

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django signing key | `django-insecure-…` (change in production) |
| `DEBUG` | Debug mode, must be `True`/`False` exactly | `True` |
| `ALLOWED_HOSTS` | Comma-separated permitted hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Neon Postgres connection string | `postgresql://…?sslmode=require` |

`.env` is git-ignored. **`.env.example` is tracked** — keep placeholders in it, never real
credentials.

---

## 6. How to log in (by role)

Go to **http://127.0.0.1:8000/accounts/login/** and enter a username and password.
All seeded accounts share one password.

### Demo credentials (local development only)

| Role | Username | Password | You land on |
|---|---|---|---|
| **Supplier** | `supplier1` … `supplier5` | `EcoLoop@123` | Supplier dashboard |
| **Buyer** | `buyer1` … `buyer5` | `EcoLoop@123` | Buyer dashboard |
| **Admin** | `admin` | `EcoLoop@123` | Admin panel |

- App login → `/accounts/login/`
- Admin panel → **http://127.0.0.1:8000/admin/** (username `admin`, password `EcoLoop@123`)

### Option A — log in as an existing demo user

1. Open `/accounts/login/`.
2. Type e.g. `supplier1` / `EcoLoop@123` → **Login**. You are redirected to `/dashboard/`.
3. Log out from the avatar dropdown in the navbar (top right).

### Option B — register a new account with a specific role

1. Open `/accounts/register/` (or click **Get Started** in the navbar).
2. Fill in username, name, email and password.
3. **Choose the role** — this is the step that decides your experience:
   - **Supplier** → you get the *Add Listing* button and receive purchase requests.
   - **Buyer** → you get *Favourites*, *AI Match* and can submit purchase requests.
4. Complete company, industry, city and state → **Register**. You are logged in immediately and land
   on your role's dashboard.

> Role behaviour is enforced server-side: a buyer trying to open `/marketplace/listing/add/` is
> bounced back with an error message, and suppliers cannot submit requests.

### Option C — admin

1. Go to `/admin/`.
2. Sign in with `admin` / `EcoLoop@123`.
3. Manage users, profiles, categories, listings, purchase requests and contact messages.

---

## 7. What each role can do

| Capability | Supplier | Buyer | Admin |
|---|:---:|:---:|:---:|
| Browse / search / filter marketplace | ✅ | ✅ | ✅ |
| Create, edit, delete listings | ✅ | ❌ | ✅ |
| Submit purchase requests | ❌ | ✅ | ✅ |
| Accept / reject / complete requests | ✅ (own listings) | ❌ | ✅ |
| Cancel a pending request | ❌ | ✅ | ✅ |
| Favourites & AI recommendations | ✅ | ✅ | ✅ |
| Category suggester | ✅ | ✅ | ✅ |
| Transaction history | ✅ | ✅ | ✅ |
| Analytics dashboard | ✅ | ✅ | ✅ |
| Django admin (`/admin/`) | ❌ | ❌ | ✅ |

Supplier dashboard shows: total/active listings, pending requests, completed exchanges, latest
listings and incoming requests. Buyer dashboard shows: total/pending requests, completed exchanges,
saved listings, recent requests and favourites.

---

## 8. Project structure

```
EcoLoop/
├── config/           Settings (settings/urls/wsgi/asgi)
├── accounts/         Registration, login, profiles, role dashboards, signal, backfill migration
├── marketplace/      Listings, purchase requests, favourites, contact, seed_data, image tag
├── recommendations/  Recommendation + category-suggest views/forms
├── analytics/        KPI aggregation + Chart.js dashboard
├── core/             Home, about, error pages, /dashboard/ route
├── ml/recommender.py TF-IDF + multi-factor scoring and the category classifier
├── templates/        All HTML (base.html + per-app templates)
├── static/           css/ js/ images/ (category art lives in images/categories/)
├── media/            Uploaded listing photos and avatars
├── docs/             architecture.md, project_report.md, testing.md
└── requirements.txt
```

URL map: `/` · `/dashboard/` · `/accounts/*` · `/marketplace/*` · `/recommendations/*` ·
`/analytics/*` · `/admin/`

---

## 9. Data model

| Table | Purpose |
|---|---|
| `auth.User` | Login identity (Django's built-in user) |
| `accounts.UserProfile` | role, company, industry, phone, city/state, address, website, bio, avatar, `is_verified` |
| `marketplace.MaterialCategory` | 8 seeded categories with slug, icon, colour |
| `marketplace.WasteListing` | supplier, category, description, quantity, price/kg, grade A–D, city/state, image, status |
| `marketplace.PurchaseRequest` | buyer, listing, requested qty, proposed price, message, status workflow |
| `marketplace.FavouriteListing` | unique (user, listing) |
| `marketplace.ContactMessage` | contact form inbox (admin-readable) |

Statuses — listing: `available → reserved → sold → inactive`;
request: `pending → accepted / rejected / completed / cancelled`.

---

## 10. AI recommendation engine

`ml/recommender.py` — content-based, no pretrained model, every score is explainable:

| Factor | Weight | Method |
|---|---|---|
| Text similarity | 35% | TF-IDF (1–2 grams) + cosine similarity over title/category/description |
| Category match | 25% | Exact category = 1.0, unspecified = 0.5, mismatch = 0.1 |
| Quantity | 15% | Full credit if stock ≥ requested, otherwise proportional |
| Location | 15% | 1.0 preferred state, 0.3 otherwise, 0.5 if unspecified |
| Price | 10% | Full credit within budget, decays with overage |

Each result renders the score, per-factor bars, and reasons such as *"Within budget (₹40 ≤ ₹50/kg)"*.

**Category suggester** — TF-IDF + Logistic Regression trained on an 18-sample labelled set
(Plastic, Metal, Paper, Glass, Textile, Rubber, Organic By-products, Other Industrial); returns the
predicted label and confidence. Heuristic by design, stated as such in the UI.

---

## 11. UI and image assets

**Category images use a file convention — no database field, no migration.**

Drop a file into `static/images/categories/` named after the category slug:

```
static/images/categories/plastic.webp        # ← served to browsers
static/images/categories/plastic.png         # ← your source art, kept but never served
```

- Extension precedence (first match wins): `.webp` `.jpg` `.jpeg` `.png` `.svg`
- Sizes: source 1500×975 is fine; generated WebPs are 800×520 (~746 KB total for all 8 vs 17.8 MB)
- No file → the card falls back to the category's Bootstrap icon, so nothing ever breaks
- On the artwork the **category name is displayed as a chip** (the icon overlay is reserved for the
  no-image fallback)
- Current slugs: `plastic`, `metal`, `glass`, `textile`, `paper-cardboard`, `rubber`,
  `organic-by-products`, `other-industrial`
- Full instructions live in `static/images/categories/README.txt`

**Motion:** `.reveal*` classes drive scroll reveals; `.land` / `.land-pending` drive the staggered
landing transition applied by `static/js/main.js`. Both respect
`prefers-reduced-motion`.

---

## 12. Testing

```bash
python manage.py test accounts marketplace --noinput --verbosity=2
```

**48 tests, all passing** — `marketplace` (42: marketplace browsing, registration/login, role
permissions, request workflow, recommender scoring) and `accounts` (6: profile signal behaviour and
dashboard access).

Tests create and destroy a temporary `test_neondb` database. **On Neon, run them against the direct
endpoint** — the pooler holds a session that blocks `CREATE/DROP DATABASE`:

```bash
RAW=$(python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.environ['DATABASE_URL'])")
DATABASE_URL="${RAW/-pooler/}" python manage.py test accounts marketplace --noinput
```

Without `DATABASE_URL` the suite runs against SQLite and needs none of this.

---

## 13. Troubleshooting

| Symptom | Fix |
|---|---|
| `DisallowedHost: Invalid HTTP_HOST header` | Add the host to `ALLOWED_HOSTS` in `.env` |
| `database "test_neondb" is being accessed by other users` | Drop it with `DROP DATABASE test_neondb WITH (FORCE)`, or use `--keepdb` on the direct endpoint |
| Test run prompts for input and dies with `EOFError` | Pass `--noinput` |
| Connection timeouts / very slow test runs | Neon compute was cold; retry, or use the direct endpoint |
| A new category image doesn't appear | Filenames must match the slug; a `.webp` overrides `.png`/`.svg` — regenerate or delete it |
| `DATABASE_URL` empty | Falls back to SQLite by design; set it in `.env` to use Neon |

---

## 14. Security notes

- **Change the admin password** — `EcoLoop@123` is a well-known demo credential published in this
  file and the database is cloud-hosted: `python manage.py changepassword admin`.
- `.env` is git-ignored; `.env.example` holds placeholders only (a real credential that was pasted
  there was removed before any commit).
- Roles are enforced in views, not just hidden in templates.
- CSRF protection is enabled on all POST forms (Django middleware). The AJAX favourite toggle uses a
  `GET` request carrying only `X-Requested-With` — see limitation 2 below.
- For deployment: set `DEBUG=False`, tighten `ALLOWED_HOSTS`, collect static files, and serve them
  through a CDN or WhiteNoise (not wired up yet).

---

## 15. Known limitations and roadmap

Honest gaps found during review, in rough priority order:

1. **Request state machine** — `update_request_status` accepts any status transition (a pending
   request can jump straight to `completed`) and listing quantity is never decremented, so stock can
   be sold repeatedly.
2. **Favourite toggle mutates state over GET** — `toggle_favourite` accepts a plain `GET`, so a
   cross-site request could flip a user's favourites, and the `csrfToken` lookup in `main.js` is dead
   code. Should be `POST` with the CSRF token.
3. **Open redirect on login** — `next` is taken from `request.GET` without validating the path.
4. **Test coverage** — `recommendations`, `analytics` and `core` have no dedicated tests.
5. **Deployment** — no WhiteNoise/`collectstatic` pipeline; static files are served by `runserver`.
6. **Admin user profiles** — handled by signal + backfill, but profile fields (role, company) still
   need filling in via the admin for staff accounts.
7. **ML scale** — the recommender re-vectorises per request and the classifier trains on 18 samples;
   fine for demo scale, not for production volume.
8. **N+1 risk on dashboards** — several `count()` queries could be aggregated.
