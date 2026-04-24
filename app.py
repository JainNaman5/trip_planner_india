"""
app.py - Flask backend for Trip Planner India.
Serves Jinja2 templates and uses ML model for recommendations.
"""
from flask import Flask, render_template, request, jsonify
import os, json
from ml_model import TripRecommender

app = Flask(__name__)
recommender = TripRecommender()

IMAGES = {
    "Delhi":"https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=800&q=80",
    "Mumbai":"https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=800&q=80",
    "Jaipur":"https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=800&q=80",
    "Agra":"https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=800&q=80",
    "Varanasi":"https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=800&q=80",
    "Goa":"https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
    "Udaipur":"https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=800&q=80",
    "Shimla":"https://images.unsplash.com/photo-1597074866923-dc0589150458?auto=format&fit=crop&w=800&q=80",
    "Kolkata":"https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=800&q=80",
    "Kochi":"https://images.unsplash.com/photo-1602158123539-d8e1c2dee5f9?auto=format&fit=crop&w=800&q=80",
    "Leh":"https://images.unsplash.com/photo-1626015365107-52a25403ee61?auto=format&fit=crop&w=800&q=80",
}
DEFAULT_IMG = "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=800&q=80"

MODE_ICONS = {"Car":"directions_car","Bus":"directions_bus","Train":"train","Flight":"flight"}
BUDGET_LABELS = {"low":"Budget","medium":"Standard","high":"Luxury"}
TRIP_LABELS = {"popular":"Heritage","balanced":"Spiritual","nearby":"Adventure"}

def img(city):
    return IMAGES.get(city, DEFAULT_IMG)

@app.route("/")
def index():
    locations = recommender.get_all_city_names()
    return render_template("index.html", active_page="home", locations=locations)

@app.route("/explore")
def explore():
    location = request.args.get("location", "Jaipur")
    budget = request.args.get("budget", "medium")
    trip_type = request.args.get("trip_type", "balanced")

    result = recommender.get_recommendations(location, budget, trip_type)
    if result is None:
        locations = recommender.get_all_city_names()
        return render_template("index.html", active_page="home", locations=locations,
                               error=f"City '{location}' not found. Try Delhi, Mumbai, or Jaipur.")

    nearby = []
    for p in result["nearby"][:8]:
        top_attr = p["attractions"][0] if p["attractions"] else None
        transport_list = []
        for t in p["transport"]:
            transport_list.append({
                "mode": t["mode"], "icon": MODE_ICONS.get(t["mode"],"directions_car"),
                "price_display": f"₹{t['price_inr']:,}", "duration": f"{t['duration_hrs']}h"
            })
        nearby.append({
            **p, "image": img(p["city"]),
            "description": top_attr["description"] if top_attr else f"Explore {p['city']}",
            "transport": transport_list,
        })

    return render_template("explore.html", active_page="explore",
        origin=result["origin"], nearby=nearby, budget=budget, trip_type=trip_type,
        budget_label=BUDGET_LABELS.get(budget,"Standard"),
        trip_type_label=TRIP_LABELS.get(trip_type,"Spiritual"),
        cluster_theme=result["cluster_theme"])

@app.route("/stays")
def stays():
    location = request.args.get("location", "Jaipur")
    dest = request.args.get("dest", "")
    budget = request.args.get("budget", "medium")
    trip_type = request.args.get("trip_type", "balanced")

    result = recommender.get_recommendations(location, budget, trip_type)
    if result is None:
        return render_template("index.html", active_page="home",
                               locations=recommender.get_all_city_names(),
                               error=f"City '{location}' not found.")

    # Find specific destination or use top result
    target = None
    for p in result["nearby"]:
        if p["city"].lower() == dest.lower():
            target = p
            break
    if not target and result["nearby"]:
        target = result["nearby"][0]

    transport = []
    stays_list = []
    dest_city = dest_state = ""
    if target:
        dest_city = target["city"]
        dest_state = target["state"]
        for t in target["transport"]:
            transport.append({
                "mode": t["mode"], "icon": MODE_ICONS.get(t["mode"],"directions_car"),
                "price_display": f"₹{t['price_inr']:,}", "duration": f"{t['duration_hrs']}h"
            })
        stays_list = target["stays"]

    return render_template("stays.html", active_page="stays",
        origin=location, dest_city=dest_city, dest_state=dest_state,
        dest_image=img(dest_city), transport=transport, stays=stays_list,
        cluster_theme=result["cluster_theme"])

@app.route("/planner")
def planner():
    location = request.args.get("location", "Jaipur")
    budget = request.args.get("budget", "medium")
    trip_type = request.args.get("trip_type", "balanced")

    result = recommender.get_recommendations(location, budget, trip_type)
    if result is None:
        return render_template("index.html", active_page="home",
                               locations=recommender.get_all_city_names(),
                               error=f"City '{location}' not found.")

    origin = result["origin"]
    itinerary = []
    trip_cities = [origin] + result["nearby"][:5]
    for day, c in enumerate(trip_cities, 1):
        city_name = c.get("city", c.get("name",""))
        highlight = c["attractions"][0]["name"] if c.get("attractions") else f"Explore {city_name}"
        hotel = f"Stay: {c['stays'][0]['name']}" if c.get("stays") else ("Starting point" if day==1 else "")
        itinerary.append({
            "day": day, "city": city_name, "highlight": highlight,
            "hotel": hotel, "coordinates": [c["lat"], c["lng"]]
        })

    center_lat = sum(i["coordinates"][0] for i in itinerary) / len(itinerary)
    center_lng = sum(i["coordinates"][1] for i in itinerary) / len(itinerary)

    return render_template("planner.html", active_page="planner",
        origin=location, trip_name=f"{location} Explorer Route",
        itinerary=itinerary, itinerary_json=json.dumps(itinerary),
        center_lat=center_lat, center_lng=center_lng)

# Keep API endpoints for compatibility with the original React HTML
@app.route("/api/locations")
def api_locations():
    return jsonify({"options": recommender.get_all_city_names()})

# Train the ML model when the module loads (works with both dev server and WSGI)
recommender.fit()

if __name__ == "__main__":
    print("=" * 50)
    print("  Trip Planner India")
    print("  Flask + Machine Learning Backend")
    print("=" * 50)
    print(f"\n  Open http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)

