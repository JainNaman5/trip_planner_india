"""
seed_data.py - Creates and populates the SQLite database from the dataset CSV.
Dataset: https://github.com/MAHESHPATIDAR2615/Travel-Dataset-Guide-to-India-s-Must-see-Places
Run once: python seed_data.py
"""
import sqlite3, os, csv, math, random

random.seed(42)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trip_planner.db")
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Top_Indian_Places_to_Visit.csv")

# Approximate lat/lng for cities (used for KNN and map)
CITY_COORDS = {
    "Delhi":  (28.6139, 77.2090), "New Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777), "Jaipur": (26.9124, 75.7873),
    "Agra": (27.1767, 78.0081), "Varanasi": (25.3176, 82.9739),
    "Goa": (15.2993, 73.9512), "Udaipur": (24.5854, 73.7125),
    "Shimla": (31.1048, 77.1734), "Manali": (32.2396, 77.1887),
    "Rishikesh": (30.0869, 78.2676), "Amritsar": (31.6340, 74.8723),
    "Bangalore": (12.9716, 77.5946), "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707), "Hyderabad": (17.3850, 78.4867),
    "Kochi": (9.9312, 76.2673), "Mysore": (12.2958, 76.6394),
    "Ooty": (11.4102, 76.6950), "Puducherry": (11.9416, 79.8083),
    "Munnar": (10.0889, 77.0595), "Kolkata": (22.5726, 88.3639),
    "Darjeeling": (27.0360, 88.2627), "Gangtok": (27.3389, 88.6065),
    "Puri": (19.8135, 85.8312), "Bhopal": (23.2599, 77.4126),
    "Jodhpur": (26.2389, 73.0243), "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714), "Leh": (34.1526, 77.5771),
    "Alappuzha": (9.4981, 76.3388), "Khajuraho": (24.8318, 79.9199),
    "Hampi": (15.3350, 76.4600), "Coorg": (12.3375, 75.8069),
    "Lucknow": (26.8467, 80.9462), "Chandigarh": (30.7333, 76.7794),
    "Srinagar": (34.0837, 74.7973), "Haridwar": (29.9457, 78.1642),
    "Nainital": (29.3803, 79.4636), "Dehradun": (30.3165, 78.0322),
    "Mathura": (27.4924, 77.6737), "Vrindavan": (27.5831, 77.7000),
    "Jaisalmer": (26.9157, 70.9083), "Bikaner": (28.0229, 73.3119),
    "Lonavala": (18.7557, 73.4091), "Nashik": (20.0112, 73.7903),
    "Aurangabad": (19.8762, 75.3433), "Madurai": (9.9252, 78.1198),
    "Rameswaram": (9.2876, 79.3129), "Kanyakumari": (8.0883, 77.5385),
    "Kodaikanal": (10.2381, 77.4892), "Thanjavur": (10.7870, 79.1378),
    "Mahabalipuram": (12.6208, 80.1946), "Visakhapatnam": (17.6868, 83.2185),
    "Vijayawada": (16.5062, 80.6480), "Tirupati": (13.6288, 79.4192),
    "Coimbatore": (11.0168, 76.9558), "Mangalore": (12.9141, 74.8560),
    "Guwahati": (26.1445, 91.7362), "Ranchi": (23.3441, 85.3096),
    "Patna": (25.6093, 85.1376), "Indore": (22.7196, 75.8577),
    "Gwalior": (26.2183, 78.1828), "Ujjain": (23.1765, 75.7885),
    "Allahabad": (25.4358, 81.8463), "Jhansi": (25.4484, 78.5685),
    "Jammu": (32.7266, 74.8570), "Mussoorie": (30.4598, 78.0644),
    "Pushkar": (26.4897, 74.5511), "Ajmer": (26.4499, 74.6399),
    "Chittorgarh": (24.8887, 74.6269), "Mount Abu": (24.5926, 72.7156),
    "Shirdi": (19.7662, 74.4776), "Kolhapur": (16.7050, 74.2433),
    "Dwarka": (22.2394, 68.9678), "Somnath": (20.8880, 70.4012),
    "Bodh Gaya": (24.6961, 84.9911), "Konark": (19.8876, 86.0945),
    "Bhubaneswar": (20.2961, 85.8245), "Nagpur": (21.1458, 79.0882),
    "Pahalgam": (34.0161, 75.3150), "Badrinath": (30.7433, 79.4938),
    "Kedarnath": (30.7346, 79.0669), "Gurugram": (28.4595, 77.0266),
    "Sawai Madhopur": (26.0224, 76.3569), "Fatehpur Sikri": (27.0945, 77.6612),
    "Sarnath": (25.3715, 83.0247), "Port Blair": (11.6234, 92.7265),
    "Havelock Island": (12.0167, 93.0167), "Auroville": (12.0057, 79.8106),
    "Cherrapunji": (25.2700, 91.7320), "Tawang": (27.5860, 91.8596),
    "Agartala": (23.8315, 91.2868), "Kaziranga": (26.5775, 93.1711),
    "Diu": (20.7144, 70.9874), "Deoghar": (24.4854, 86.6944),
    "Wayanad": (11.6854, 76.1320), "Thekkady": (9.6000, 77.1600),
    "Varkala": (8.7379, 76.7163), "Kovalam": (8.3988, 76.9784),
    "Kannur": (11.8745, 75.3704), "Pelling": (27.2989, 88.2318),
    "Namchi": (27.1667, 88.3500), "Ravangla": (27.3078, 88.3631),
    "Gokarna": (14.5479, 74.3188), "Chikmagalur": (13.3153, 75.7754),
    "Manikaran": (32.0453, 77.3494), "Spiti Valley": (32.2461, 78.0188),
    "Kullu": (31.9579, 77.1096), "Dalhousie": (32.5387, 75.9700),
    "Matheran": (18.9866, 73.2681), "Tarkarli": (16.0145, 73.4648),
}

def get_coords(city):
    """Get approximate coordinates for a city."""
    city_clean = city.strip().title()
    if city_clean in CITY_COORDS:
        return CITY_COORDS[city_clean]
    # Try partial match
    for k, v in CITY_COORDS.items():
        if city_clean.lower() in k.lower() or k.lower() in city_clean.lower():
            return v
    # Default to center of India
    return (22.0 + random.uniform(-3, 3), 78.0 + random.uniform(-5, 5))

def create_tables(cur):
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, state TEXT NOT NULL,
        zone TEXT, lat REAL NOT NULL, lng REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS attractions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, city_id INTEGER NOT NULL,
        type TEXT, significance TEXT, popularity REAL DEFAULT 5,
        google_rating REAL, entrance_fee INTEGER DEFAULT 0,
        best_time TEXT, description TEXT,
        lat REAL, lng REAL,
        FOREIGN KEY (city_id) REFERENCES cities(id)
    );
    CREATE TABLE IF NOT EXISTS transport (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_city_id INTEGER NOT NULL, to_city_id INTEGER NOT NULL,
        mode TEXT NOT NULL, price_inr INTEGER NOT NULL,
        duration_hrs REAL NOT NULL,
        FOREIGN KEY (from_city_id) REFERENCES cities(id),
        FOREIGN KEY (to_city_id) REFERENCES cities(id)
    );
    CREATE TABLE IF NOT EXISTS stays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL, name TEXT NOT NULL,
        type TEXT NOT NULL, price_per_night INTEGER NOT NULL,
        rating REAL DEFAULT 4.0,
        FOREIGN KEY (city_id) REFERENCES cities(id)
    );
    """)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    create_tables(cur)

    # --- Parse CSV ---
    city_map = {}  # (city, state) -> city_id
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            city = row["City"].strip()
            state = row["State"].strip()
            zone = row["Zone"].strip()
            key = (city.lower(), state.lower())

            if key not in city_map:
                lat, lng = get_coords(city)
                cur.execute("INSERT INTO cities (name, state, zone, lat, lng) VALUES (?,?,?,?,?)",
                            (city, state, zone, lat, lng))
                city_map[key] = cur.lastrowid

            city_id = city_map[key]
            lat, lng = get_coords(city)
            try:
                rating = float(row["Google review rating"])
            except:
                rating = 4.0
            try:
                fee = int(float(row["Entrance Fee in INR"]))
            except:
                fee = 0
            try:
                reviews = float(row["Number of google review in lakhs"])
                popularity = min(10, reviews * 2 + rating)
            except:
                popularity = rating

            cur.execute("""INSERT INTO attractions
                (name, city_id, type, significance, popularity, google_rating,
                 entrance_fee, best_time, description, lat, lng)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (row["Name"].strip(), city_id, row["Type"].strip(),
                 row["Significance"].strip(), round(popularity, 1), rating,
                 fee, row["Best Time to visit"].strip(),
                 f"{row['Name'].strip()} - a {row['Type'].strip().lower()} in {city}, {state}. Significance: {row['Significance'].strip()}. Rating: {rating}/5.",
                 lat + random.uniform(-0.02, 0.02), lng + random.uniform(-0.02, 0.02)))

    # --- Generate transport between nearby cities ---
    cities = cur.execute("SELECT id, name, lat, lng FROM cities").fetchall()
    transport_rows = []
    for i, c1 in enumerate(cities):
        for j, c2 in enumerate(cities):
            if i == j: continue
            dist = haversine(c1[2], c1[3], c2[2], c2[3])
            if dist > 1200: continue
            transport_rows.append((c1[0], c2[0], "Car", int(dist * 8), round(dist / 60, 1)))
            transport_rows.append((c1[0], c2[0], "Bus", int(dist * 3), round(dist / 45, 1)))
            if dist > 50:
                transport_rows.append((c1[0], c2[0], "Train", int(dist * 2), round(dist / 70, 1)))
            if dist > 400:
                transport_rows.append((c1[0], c2[0], "Flight", int(1500 + dist * 3), round(dist / 700 + 1, 1)))
    cur.executemany("INSERT INTO transport (from_city_id, to_city_id, mode, price_inr, duration_hrs) VALUES (?,?,?,?,?)",
                    transport_rows)

    # --- Generate stays for each city ---
    templates = [
        ("budget", ["Backpacker Hostel", "Budget Inn", "Guest House"], 500, 1500, 3.5),
        ("mid_range", ["Comfort Hotel", "Heritage Stay", "City Hotel"], 2000, 5000, 4.0),
        ("luxury", ["Grand Palace Hotel", "Luxury Resort", "Premium Suite"], 6000, 15000, 4.5),
    ]
    stay_rows = []
    for cid, cname, _, _ in cities:
        for typ, names, lo, hi, base_r in templates:
            name = f"{random.choice(names)} {cname}"
            stay_rows.append((cid, name, typ, random.randint(lo, hi), round(min(base_r + random.uniform(-0.3, 0.5), 5.0), 1)))
    cur.executemany("INSERT INTO stays (city_id, name, type, price_per_night, rating) VALUES (?,?,?,?,?)", stay_rows)

    conn.commit()
    for t in ["cities", "attractions", "transport", "stays"]:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t}: {cur.fetchone()[0]} rows")
    conn.close()
    print(f"\nDatabase created at {DB_PATH}")
    print(f"Source: {CSV_PATH}")

if __name__ == "__main__":
    main()
