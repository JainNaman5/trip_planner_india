"""
ml_model.py - Machine Learning recommendation engine for Trip Planner India.
Uses KNN for nearest-city lookup and K-Means for regional clustering.
"""
import sqlite3, math, os
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trip_planner.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lng points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


class TripRecommender:
    """ML-powered trip recommendation engine."""

    CLUSTER_THEMES = {
        0: "Heritage & Culture",
        1: "Beaches & Coastal",
        2: "Mountains & Adventure",
        3: "Spiritual & Pilgrimage",
        4: "Nature & Wildlife",
    }

    def __init__(self):
        self.knn_model = None
        self.kmeans_model = None
        self.scaler = StandardScaler()
        self.cities = []
        self.city_coords = None

    def fit(self):
        """Train ML models on city data from the database."""
        conn = get_db()
        rows = conn.execute("SELECT id, name, state, lat, lng FROM cities").fetchall()
        conn.close()

        self.cities = [dict(r) for r in rows]
        coords = np.array([[c["lat"], c["lng"]] for c in self.cities])
        self.city_coords = coords

        # Standardise coordinates for KNN
        scaled = self.scaler.fit_transform(coords)

        # KNN model — find nearest cities by geography
        k = min(len(self.cities), 25)
        self.knn_model = NearestNeighbors(n_neighbors=k, metric="euclidean")
        self.knn_model.fit(scaled)

        # K-Means clustering — group cities into regional clusters
        n_clusters = min(5, len(self.cities))
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.kmeans_model.fit(scaled)

        # Assign cluster labels
        labels = self.kmeans_model.labels_
        for i, city in enumerate(self.cities):
            city["cluster"] = int(labels[i])

        print(f"[ML] Trained KNN (k={k}) and KMeans ({n_clusters} clusters) on {len(self.cities)} cities")

    def _find_city(self, name):
        """Lookup city by name (case-insensitive)."""
        name_lower = name.lower().strip()
        for c in self.cities:
            if c["name"].lower() == name_lower:
                return c
        # Partial match fallback
        for c in self.cities:
            if name_lower in c["name"].lower() or c["name"].lower() in name_lower:
                return c
        return None

    def get_nearby_cities(self, lat, lng, k=10):
        """Use KNN to find the k nearest cities within 500km of a coordinate."""
        n = min(k + 15, len(self.cities))  # Fetch extra to filter by real distance
        point = self.scaler.transform([[lat, lng]])
        distances, indices = self.knn_model.kneighbors(point, n_neighbors=n)
        results = []
        for dist_val, idx in zip(distances[0], indices[0]):
            city = self.cities[idx]
            real_dist = haversine(lat, lng, city["lat"], city["lng"])
            if 10 < real_dist <= 500:  # Skip origin and too-far cities
                results.append({**city, "distance_km": round(real_dist)})
        results.sort(key=lambda x: x["distance_km"])
        return results[:k]

    def get_recommendations(self, city_name, budget="medium", trip_type="balanced"):
        """Full recommendation pipeline for a given city."""
        origin = self._find_city(city_name)
        if not origin:
            return None

        # 1. KNN — nearby cities
        nearby = self.get_nearby_cities(origin["lat"], origin["lng"], k=10)

        # 2. Get attractions for nearby cities
        conn = get_db()
        nearby_ids = [c["id"] for c in nearby]
        if not nearby_ids:
            conn.close()
            return {"origin": origin, "nearby": [], "cluster_id": 0, "cluster_theme": "General"}

        placeholders = ",".join("?" * len(nearby_ids))
        attractions = conn.execute(
            f"SELECT * FROM attractions WHERE city_id IN ({placeholders}) ORDER BY popularity DESC",
            nearby_ids
        ).fetchall()
        attractions = [dict(a) for a in attractions]

        # 3. Build scored nearby list
        scored = []
        for city in nearby:
            city_attractions = [a for a in attractions if a["city_id"] == city["id"]]
            avg_pop = (sum(a["popularity"] for a in city_attractions) / len(city_attractions)) if city_attractions else 0
            avg_rating = (sum(a.get("google_rating", 4.0) for a in city_attractions) / len(city_attractions)) if city_attractions else 4.0
            num_attractions = len(city_attractions)

            # ML Score: weighted combo of distance, popularity, rating, and variety
            dist_score = max(0, 100 - city["distance_km"] * 0.12)
            pop_score = min(avg_pop * 8, 50)
            rating_score = (avg_rating - 3.0) * 15  # 0-30 range
            variety_score = min(num_attractions * 5, 20)

            # Trip-type weighting adjustments
            sig_types = [a.get("significance", "") for a in city_attractions]
            if trip_type == "nearby":
                # Adventure: prefer closer, nature/adventure spots
                adventure_bonus = sum(5 for s in sig_types if s in ("Adventure","Nature","Wildlife","Recreational")) 
                match_score = int(dist_score * 0.6 + pop_score * 0.15 + rating_score * 0.1 + variety_score * 0.05 + adventure_bonus)
            elif trip_type == "popular":
                # Heritage: prefer historical, high-rated, popular
                heritage_bonus = sum(5 for s in sig_types if s in ("Historical","Architectural","Cultural","Archaeological"))
                match_score = int(dist_score * 0.2 + pop_score * 0.4 + rating_score * 0.2 + variety_score * 0.1 + heritage_bonus)
            else:
                # Spiritual/balanced: prefer religious, spiritual spots
                spiritual_bonus = sum(5 for s in sig_types if s in ("Religious","Spiritual"))
                match_score = int(dist_score * 0.35 + pop_score * 0.25 + rating_score * 0.2 + variety_score * 0.1 + spiritual_bonus)

            # Budget relevance: penalize expensive attractions for budget travelers
            if budget == "low":
                avg_fee = (sum(a.get("entrance_fee", 0) for a in city_attractions) / max(len(city_attractions), 1))
                if avg_fee > 200:
                    match_score -= 10
            elif budget == "high":
                match_score += 5  # Luxury travelers get a small boost for popular spots

            match_score = max(15, min(match_score, 98))

            # Transport options
            transport = conn.execute(
                "SELECT mode, price_inr, duration_hrs FROM transport WHERE from_city_id=? AND to_city_id=?",
                (origin["id"], city["id"])
            ).fetchall()

            # Get all stay options (budget, mid-range, luxury) for the city
            stays = conn.execute(
                "SELECT name, type, price_per_night, rating FROM stays WHERE city_id=? ORDER BY price_per_night",
                (city["id"],)
            ).fetchall()

            scored.append({
                "city": city["name"],
                "state": city["state"],
                "lat": city["lat"],
                "lng": city["lng"],
                "distance_km": city["distance_km"],
                "match_score": match_score,
                "attractions": [{"name": a["name"], "category": a.get("type", ""),
                                 "popularity": a["popularity"], "description": a.get("description", "")}
                                for a in city_attractions[:5]],
                "transport": [{"mode": dict(t)["mode"],
                               "price_inr": dict(t)["price_inr"],
                               "duration_hrs": dict(t)["duration_hrs"]}
                              for t in transport],
                "stays": [{"name": dict(s)["name"], "type": dict(s)["type"],
                           "price_per_night": dict(s)["price_per_night"],
                           "rating": dict(s)["rating"]}
                          for s in stays],
            })

        conn.close()

        # Sort by match score descending
        scored.sort(key=lambda x: x["match_score"], reverse=True)

        cluster_id = origin.get("cluster", 0)
        return {
            "origin": origin,
            "nearby": scored,
            "cluster_id": cluster_id,
            "cluster_theme": self.CLUSTER_THEMES.get(cluster_id, "General"),
        }

    def get_all_city_names(self):
        """Return list of all city names for autocomplete."""
        conn = get_db()
        cities = conn.execute("SELECT name, state FROM cities ORDER BY name").fetchall()
        states = conn.execute("SELECT DISTINCT state FROM cities ORDER BY state").fetchall()
        conn.close()
        options = []
        for c in cities:
            options.append({"value": c["name"], "label": f"{c['name']}, {c['state']}", "type": "city"})
        for s in states:
            options.append({"value": s["state"], "label": s["state"], "type": "state"})
        return options
