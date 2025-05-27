import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import random


vectorizer = pickle.load(open("app/vectorizer.pkl", "rb"))
tfidf_matrix = pickle.load(open("app/tfidf_matrix.pkl", "rb"))
df = pickle.load(open("app/df.pkl", "rb"))


EXCLUDE_KEYWORDS = ["garlic", "cheese", "onion", "egg", "meat"]
VEGAN_EXCLUDES = ["chicken", "meat", "egg", "beef", "fish", "lamb", "pork", "bacon", "turkey", "kebab"]
NO_MEAT_EXCLUDES = ["chicken", "meat", "beef", "fish", "lamb", "pork", "bacon", "turkey", "kebab"]

def extract_filters(user_input: str):
    include = []
    exclude = []
    input_lower = user_input.lower()

    if "vegan" in input_lower:
        exclude.extend(VEGAN_EXCLUDES)
        include.append("vegan")

    if "without meat" in input_lower or "no meat" in input_lower:
        exclude.extend(NO_MEAT_EXCLUDES)

    for word in EXCLUDE_KEYWORDS:
        if re.search(rf"\b(no|without|exclude)\s+{word}\b", input_lower):
            exclude.append(word)
        elif word in input_lower:
            include.append(word)

    return include, list(set(exclude))

def detect_direct_category(user_input: str):
    if "dessert" in user_input.lower():
        return "dessert"
    return None

def get_top_n_recommendations(user_input, budget, n=3):
    direct_category = detect_direct_category(user_input)
    user_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()

    include, exclude = extract_filters(user_input)
    sorted_indices = similarities.argsort()[::-1]

    top_matches = []

    for idx in sorted_indices:
        row = df.iloc[idx]
        desc = row['Describe'].lower()

        if "vegan" in include:
            if row["Veg_Non"].lower() != "veg":
                continue
            if any(bad in desc for bad in VEGAN_EXCLUDES):
                continue

        if row['price'] <= budget:
            if direct_category and row['C_Type'].lower() != direct_category:
                continue
            if all(term in desc for term in include if term != "vegan") and all(term not in desc for term in exclude):
                top_matches.append({
                    "name": row["Name"],
                    "price": row["price"],
                    "desc": row["Describe"]
                })
            if len(top_matches) >= n:
                break

    return top_matches

def get_next_unique_recommendations(user_input, budget, exclude_names, n=3):
    user_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()

    include, exclude = extract_filters(user_input)
    sorted_indices = similarities.argsort()[::-1]

    new_matches = []
    for idx in sorted_indices:
        row = df.iloc[idx]
        desc = row['Describe'].lower()

        if "vegan" in include:
            if row["Veg_Non"].lower() != "veg":
                continue
            if any(bad in desc for bad in VEGAN_EXCLUDES):
                continue

        if row['price'] <= budget:
            if row["Name"] in exclude_names:
                continue
            if all(term in desc for term in include if term != "vegan") and all(term not in desc for term in exclude):
                new_matches.append({
                    "name": row["Name"],
                    "price": row["price"],
                    "desc": row["Describe"]
                })
            if len(new_matches) >= n:
                break

    return new_matches

def get_random_desserts(n=3, max_budget=None):
    desserts = df[df['C_Type'].str.lower() == 'dessert']
    if max_budget is not None:
        desserts = desserts[desserts['price'] <= max_budget]
    if desserts.empty:
        return []
    sampled = desserts.sample(n=min(n, len(desserts)))
    return [{
        "name": row["Name"],
        "price": row["price"],
        "desc": row["Describe"]
    } for _, row in sampled.iterrows()]
