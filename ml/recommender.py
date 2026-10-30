"""
EcoLoop AI Recommendation Engine
=================================
Content-based filtering using TF-IDF cosine similarity combined with
weighted scoring for quantity, price, location, and category compatibility.

This is an honest content-based approach suitable for small datasets.
No pretrained model accuracy is claimed.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


WEIGHTS = {
    'text_similarity': 0.35,
    'category_match': 0.25,
    'location_match': 0.15,
    'quantity_score': 0.15,
    'price_score': 0.10,
}


def build_text_corpus(listings):
    """Combine title, category name, and description into a single text field."""
    texts = []
    for l in listings:
        cat_name = l.category.name if hasattr(l.category, 'name') else str(l.category)
        text = f"{l.title} {cat_name} {l.description}"
        texts.append(text.lower())
    return texts


def compute_text_similarity(query_text, corpus_texts):
    """TF-IDF cosine similarity between query and corpus."""
    if not corpus_texts:
        return np.array([])
    all_texts = [query_text.lower()] + corpus_texts
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    except Exception:
        similarities = np.zeros(len(corpus_texts))
    return similarities


def score_quantity(requested_qty, available_qty):
    """Score 1.0 if available >= requested, scales down otherwise."""
    if available_qty <= 0:
        return 0.0
    if available_qty >= requested_qty:
        return 1.0
    return float(available_qty / requested_qty)


def score_price(max_budget, listing_price):
    """Score 1.0 if listing price <= budget, scales down if over budget."""
    if max_budget is None or max_budget <= 0:
        return 0.5  # neutral when no budget specified
    if listing_price <= max_budget:
        return 1.0
    overage = (listing_price - max_budget) / max_budget
    return max(0.0, 1.0 - overage)


def score_location(preferred_state, listing_state):
    """1.0 for same state, 0.3 otherwise."""
    if not preferred_state:
        return 0.5
    return 1.0 if preferred_state.lower() == listing_state.lower() else 0.3


def get_recommendations(query_text, category_id, requested_qty, max_budget, preferred_state, listings, top_n=10):
    """
    Main recommendation function.

    Parameters
    ----------
    query_text      : str   - buyer's material description / search query
    category_id     : int   - preferred category id (None = any)
    requested_qty   : float - quantity needed in kg
    max_budget      : float - max price per kg (None = no limit)
    preferred_state : str   - preferred state (None = any)
    listings        : QuerySet - available WasteListing objects
    top_n           : int   - number of results to return

    Returns
    -------
    list of dicts with listing, score, and explanation
    """
    listings = list(listings.filter(status='available').select_related('category', 'supplier__profile'))

    if not listings:
        return []

    corpus_texts = build_text_corpus(listings)
    text_scores = compute_text_similarity(query_text, corpus_texts)

    results = []
    for i, listing in enumerate(listings):
        text_sim = float(text_scores[i]) if i < len(text_scores) else 0.0
        cat_match = 1.0 if (category_id and listing.category_id == category_id) else (0.5 if not category_id else 0.1)
        qty_score = score_quantity(float(requested_qty or 1), float(listing.quantity))
        price_score = score_price(float(max_budget) if max_budget else None, float(listing.price_per_kg))
        loc_score = score_location(preferred_state, listing.state)

        final_score = (
            WEIGHTS['text_similarity'] * text_sim +
            WEIGHTS['category_match'] * cat_match +
            WEIGHTS['quantity_score'] * qty_score +
            WEIGHTS['price_score'] * price_score +
            WEIGHTS['location_match'] * loc_score
        )

        reasons = []
        if text_sim > 0.3:
            reasons.append(f"Strong material description match ({text_sim:.0%})")
        elif text_sim > 0.1:
            reasons.append(f"Partial description match ({text_sim:.0%})")
        if cat_match == 1.0:
            reasons.append("Exact category match")
        if qty_score == 1.0:
            reasons.append(f"Sufficient quantity available ({listing.quantity} kg)")
        elif qty_score > 0:
            reasons.append(f"Partial quantity available ({listing.quantity} kg of {requested_qty} kg needed)")
        if price_score == 1.0 and max_budget:
            reasons.append(f"Within budget (₹{listing.price_per_kg}/kg ≤ ₹{max_budget}/kg)")
        if loc_score == 1.0:
            reasons.append(f"Located in {listing.state} (preferred)")

        if not reasons:
            reasons.append("General material availability")

        results.append({
            'listing': listing,
            'score': round(final_score * 100, 1),
            'explanation': '; '.join(reasons),
            'text_sim': round(text_sim * 100, 1),
            'cat_match': round(cat_match * 100, 1),
            'qty_score': round(qty_score * 100, 1),
            'price_score': round(price_score * 100, 1),
            'loc_score': round(loc_score * 100, 1),
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_n]


# ── Waste Category Classifier ──────────────────────────────────────────────────
TRAINING_DATA = [
    ("plastic scraps pellets PET HDPE polymer resin", "Plastic"),
    ("plastic film wrap packaging polyethylene", "Plastic"),
    ("PVC pipe offcuts plastic waste granules", "Plastic"),
    ("metal scrap steel iron aluminium copper", "Metal"),
    ("aluminium offcuts metal shavings brass", "Metal"),
    ("stainless steel scrap iron filings", "Metal"),
    ("paper cardboard waste corrugated boxes", "Paper & Cardboard"),
    ("newspaper waste paper pulp cardboard", "Paper & Cardboard"),
    ("glass bottles cullet broken glass", "Glass"),
    ("glass waste shards window glass", "Glass"),
    ("textile fabric offcuts cotton yarn waste", "Textile"),
    ("fabric scraps clothing waste fibre", "Textile"),
    ("rubber tyre crumb rubber waste", "Rubber"),
    ("rubber offcuts latex waste gaskets", "Rubber"),
    ("organic food waste biomass agricultural", "Organic By-products"),
    ("vegetable oil waste food processing by-product", "Organic By-products"),
    ("chemical solvent industrial waste hazardous", "Other Industrial"),
    ("electronic waste circuit board components", "Other Industrial"),
]


def get_category_classifier():
    """Train and return a simple TF-IDF + Logistic Regression classifier."""
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LogisticRegression

    texts = [t for t, _ in TRAINING_DATA]
    labels = [l for _, l in TRAINING_DATA]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=200, random_state=42)),
    ])
    pipeline.fit(texts, labels)
    return pipeline


_classifier = None


def suggest_category(text):
    """
    Suggest a material category from description text.
    Returns (predicted_label, confidence_percent).
    Note: This is a heuristic trained on a small example dataset.
    """
    global _classifier
    if _classifier is None:
        _classifier = get_category_classifier()
    proba = _classifier.predict_proba([text])[0]
    classes = _classifier.classes_
    best_idx = np.argmax(proba)
    return classes[best_idx], round(float(proba[best_idx]) * 100, 1)
