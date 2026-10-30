# EcoLoop — Project Report

## Abstract

EcoLoop is a web-based circular economy marketplace that connects industrial waste suppliers with buyers. Industries that produce reusable waste materials can list them on the platform; industries that need those materials can discover, evaluate, and request them. The system includes an AI-based recommendation engine using TF-IDF cosine similarity and multi-factor scoring to match buyers with the most relevant suppliers.

## Problem Statement

Industrial waste is a significant environmental and economic challenge. Many industries discard materials that could serve as raw inputs for other industries. The lack of a structured marketplace means that reusable materials end up in landfills while other industries pay full price for virgin raw materials.

## Project Objectives

1. Build a web platform connecting industrial waste suppliers with buyers.
2. Implement role-based accounts for suppliers, buyers, and administrators.
3. Provide a searchable, filterable marketplace for waste material listings.
4. Implement an AI recommendation engine to match buyers with suitable suppliers.
5. Track purchase requests and completed exchanges.
6. Display platform analytics using interactive charts.
7. Promote circular economy principles.

## Existing Systems

Existing industrial waste exchanges are largely manual, region-specific, or limited to specific material types. General B2B marketplaces do not specialise in waste material matching or provide AI-based recommendations for circular economy use cases.

## Proposed System

EcoLoop provides:
- A structured listing system with material categories, quantity, price, quality grade, and location.
- A content-based AI recommendation engine combining text similarity with quantity, price, location, and category scoring.
- A complete purchase request workflow.
- An analytics dashboard with live database statistics.

## System Architecture

```
Browser → Django Views → Django ORM → SQLite
                ↓
         ml/recommender.py (scikit-learn)
                ↓
         Templates (Bootstrap 5 + Chart.js)
```

## Module Descriptions

| Module          | Responsibility |
|-----------------|----------------|
| accounts        | Registration, login, profiles, dashboards |
| marketplace     | Listings, requests, favourites, contact |
| recommendations | AI matching, category suggestion |
| analytics       | Statistics, Chart.js data |
| core            | Home, about, error pages |
| ml/recommender  | TF-IDF engine, scoring functions, classifier |

## Database Design

- UserProfile: extends User with role, company, location
- MaterialCategory: name, slug, icon, color
- WasteListing: supplier, category, quantity, price, grade, location, status
- PurchaseRequest: buyer, listing, quantity, proposed price, status
- FavouriteListing: user + listing (unique together)
- ContactMessage: name, email, subject, message

## AI Recommendation Methodology

The recommendation engine is a content-based filtering system. It does not require historical interaction data, making it suitable for a new platform with limited data.

**Steps:**
1. Build a text corpus from listing title + category + description.
2. Compute TF-IDF vectors for all listings and the buyer's query.
3. Calculate cosine similarity between query and each listing.
4. Score each listing on quantity sufficiency, price compatibility, and location match.
5. Combine scores using configurable weights (text 35%, category 25%, quantity 15%, location 15%, price 10%).
6. Rank listings by final score and return top N with explanations.

**Weights are configurable** in `ml/recommender.py`. No pretrained model accuracy is claimed. The system is honest about being a heuristic approach.

**Category Classifier:** TF-IDF + Logistic Regression trained on 18 labelled examples covering 8 categories. This is a heuristic tool — users can override the suggestion.

## Technology Stack

| Component  | Technology |
|------------|------------|
| Language   | Python 3.14 |
| Framework  | Django 6.1 |
| Database   | SQLite |
| Frontend   | Bootstrap 5, Bootstrap Icons |
| AI/ML      | scikit-learn, pandas, NumPy |
| Charts     | Chart.js 4 |
| Config     | python-dotenv |

## Installation

See README.md for full setup instructions.

## Testing Results

42 automated tests were written and executed. All 42 passed.

Test categories:
- Registration and authentication (6 tests)
- Role-based permissions (4 tests)
- Listing CRUD and validation (5 tests)
- Marketplace search and filters (5 tests)
- Purchase request workflow (6 tests)
- Favourite listings (3 tests)
- Recommendation engine scoring (9 tests)
- Analytics calculations (3 tests)
- Category suggestion (1 test)

## Limitations

1. The recommendation engine is content-based and does not use collaborative filtering (no interaction history available on a new platform).
2. The category classifier is trained on 18 examples — it is a heuristic tool, not a production classifier.
3. No email notifications are implemented.
4. Image upload is stored locally; a production system would use cloud storage.
5. The CO₂ estimate (0.5 kg CO₂/kg waste diverted) is illustrative only.

## Future Enhancements

1. Collaborative filtering once sufficient interaction data is available.
2. Email notifications for request status changes.
3. In-platform messaging between suppliers and buyers.
4. Cloud storage for uploaded images.
5. Payment gateway integration.
6. Mobile application.
7. Verified industry certification badges.
