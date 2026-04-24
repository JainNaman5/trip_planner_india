"""
seed_data.py - Creates and populates the SQLite database for Trip Planner India.
Run this once: python seed_data.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trip_planner.db")

def create_tables(cur):
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS attractions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        popularity INTEGER DEFAULT 5,
        description TEXT,
        lat REAL, lng REAL,
        FOREIGN KEY (city_id) REFERENCES cities(id)
    );
    CREATE TABLE IF NOT EXISTS transport (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_city_id INTEGER NOT NULL,
        to_city_id INTEGER NOT NULL,
        mode TEXT NOT NULL,
        price_inr INTEGER NOT NULL,
        duration_hrs REAL NOT NULL,
        FOREIGN KEY (from_city_id) REFERENCES cities(id),
        FOREIGN KEY (to_city_id) REFERENCES cities(id)
    );
    CREATE TABLE IF NOT EXISTS stays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        price_per_night INTEGER NOT NULL,
        rating REAL DEFAULT 4.0,
        FOREIGN KEY (city_id) REFERENCES cities(id)
    );
    """)

# (name, state, lat, lng)
CITIES = [
    ("Delhi", "Delhi", 28.6139, 77.2090),
    ("Mumbai", "Maharashtra", 19.0760, 72.8777),
    ("Jaipur", "Rajasthan", 26.9124, 75.7873),
    ("Agra", "Uttar Pradesh", 27.1767, 78.0081),
    ("Varanasi", "Uttar Pradesh", 25.3176, 82.9739),
    ("Goa", "Goa", 15.2993, 73.9512),
    ("Udaipur", "Rajasthan", 24.5854, 73.7125),
    ("Shimla", "Himachal Pradesh", 31.1048, 77.1734),
    ("Manali", "Himachal Pradesh", 32.2396, 77.1887),
    ("Rishikesh", "Uttarakhand", 30.0869, 78.2676),
    ("Amritsar", "Punjab", 31.6340, 74.8723),
    ("Bengaluru", "Karnataka", 12.9716, 77.5946),
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707),
    ("Hyderabad", "Telangana", 17.3850, 78.4867),
    ("Kochi", "Kerala", 9.9312, 76.2673),
    ("Mysore", "Karnataka", 12.2958, 76.6394),
    ("Ooty", "Tamil Nadu", 11.4102, 76.6950),
    ("Pondicherry", "Tamil Nadu", 11.9416, 79.8083),
    ("Munnar", "Kerala", 10.0889, 77.0595),
    ("Kolkata", "West Bengal", 22.5726, 88.3639),
    ("Darjeeling", "West Bengal", 27.0360, 88.2627),
    ("Gangtok", "Sikkim", 27.3389, 88.6065),
    ("Shillong", "Meghalaya", 25.5788, 91.8933),
    ("Puri", "Odisha", 19.8135, 85.8312),
    ("Bhopal", "Madhya Pradesh", 23.2599, 77.4126),
    ("Jodhpur", "Rajasthan", 26.2389, 73.0243),
    ("Pune", "Maharashtra", 18.5204, 73.8567),
    ("Ahmedabad", "Gujarat", 23.0225, 72.5714),
    ("Leh", "Ladakh", 34.1526, 77.5771),
    ("Alleppey", "Kerala", 9.4981, 76.3388),
    ("Khajuraho", "Madhya Pradesh", 24.8318, 79.9199),
    ("Hampi", "Karnataka", 15.3350, 76.4600),
    ("Ranthambore", "Rajasthan", 26.0173, 76.5026),
    ("Coorg", "Karnataka", 12.3375, 75.8069),
    ("Andaman", "Andaman & Nicobar", 11.7401, 92.6586),
]

# (attraction_name, city_index, category, popularity, description)
ATTRACTIONS = [
    ("Red Fort", 0, "monument", 9, "Iconic Mughal-era red sandstone fort"),
    ("Qutub Minar", 0, "monument", 8, "Tallest brick minaret in the world"),
    ("India Gate", 0, "monument", 9, "War memorial and national landmark"),
    ("Lotus Temple", 0, "temple", 7, "Baha'i House of Worship shaped like a lotus"),
    ("Gateway of India", 1, "monument", 9, "Iconic arch on the Mumbai waterfront"),
    ("Marine Drive", 1, "nature", 8, "Beautiful seafront promenade"),
    ("Elephanta Caves", 1, "monument", 7, "Ancient cave temples on an island"),
    ("Hawa Mahal", 2, "monument", 9, "Palace of Winds with 953 windows"),
    ("Amber Fort", 2, "monument", 9, "Majestic hilltop fort with mirror palace"),
    ("City Palace Jaipur", 2, "monument", 8, "Royal residence with museums"),
    ("Taj Mahal", 3, "monument", 10, "One of the Seven Wonders of the World"),
    ("Agra Fort", 3, "monument", 8, "UNESCO World Heritage Mughal fortress"),
    ("Fatehpur Sikri", 3, "monument", 7, "Abandoned Mughal capital city"),
    ("Kashi Vishwanath Temple", 4, "temple", 9, "Sacred Hindu temple on the Ganges"),
    ("Dashashwamedh Ghat", 4, "temple", 9, "Famous ghat for Ganga Aarti"),
    ("Sarnath", 4, "temple", 7, "Where Buddha gave his first sermon"),
    ("Baga Beach", 5, "beach", 8, "Popular beach with nightlife"),
    ("Basilica of Bom Jesus", 5, "temple", 8, "UNESCO World Heritage church"),
    ("Dudhsagar Falls", 5, "nature", 7, "Spectacular four-tiered waterfall"),
    ("Lake Pichola", 6, "nature", 9, "Beautiful lake with palace views"),
    ("City Palace Udaipur", 6, "monument", 8, "Largest palace complex in Rajasthan"),
    ("The Ridge", 7, "nature", 7, "Open space in the heart of Shimla"),
    ("Mall Road Shimla", 7, "nature", 7, "Main shopping street with colonial charm"),
    ("Solang Valley", 8, "adventure", 8, "Adventure sports hub near Manali"),
    ("Rohtang Pass", 8, "adventure", 9, "High mountain pass with snow views"),
    ("Laxman Jhula", 9, "temple", 8, "Iconic suspension bridge over the Ganges"),
    ("Triveni Ghat", 9, "temple", 7, "Sacred confluence for ritual bathing"),
    ("Golden Temple", 10, "temple", 10, "Holiest shrine of Sikhism"),
    ("Jallianwala Bagh", 10, "monument", 9, "Historic memorial garden"),
    ("Lalbagh Garden", 11, "nature", 7, "Botanical garden with glass house"),
    ("Bangalore Palace", 11, "monument", 6, "Tudor-style palace"),
    ("Marina Beach", 12, "beach", 7, "One of the longest beaches in the world"),
    ("Kapaleeshwarar Temple", 12, "temple", 7, "Dravidian architecture temple"),
    ("Charminar", 13, "monument", 9, "Iconic mosque with four minarets"),
    ("Golconda Fort", 13, "monument", 8, "Medieval fort with acoustic marvels"),
    ("Fort Kochi", 14, "monument", 7, "Historic area with Chinese fishing nets"),
    ("Backwaters", 14, "nature", 9, "Scenic network of canals and lagoons"),
    ("Mysore Palace", 15, "monument", 9, "Stunning Indo-Saracenic palace"),
    ("Chamundi Hills", 15, "nature", 7, "Hilltop temple with city views"),
    ("Ooty Lake", 16, "nature", 7, "Artificial lake in the Nilgiris"),
    ("Botanical Gardens Ooty", 16, "nature", 7, "Terraced gardens with rare plants"),
    ("Promenade Beach", 17, "beach", 7, "French-era waterfront promenade"),
    ("Auroville", 17, "temple", 7, "Universal township and Matrimandir"),
    ("Tea Gardens Munnar", 18, "nature", 9, "Rolling hills of tea plantations"),
    ("Eravikulam NP", 18, "nature", 8, "National park with Nilgiri Tahr"),
    ("Victoria Memorial", 19, "monument", 9, "Grand marble building and museum"),
    ("Howrah Bridge", 19, "monument", 8, "Iconic cantilever bridge"),
    ("Tiger Hill", 20, "nature", 8, "Sunrise point with Kanchenjunga view"),
    ("Darjeeling Himalayan Railway", 20, "adventure", 9, "UNESCO World Heritage toy train"),
    ("Tsomgo Lake", 21, "nature", 8, "Glacial lake at 12,400 ft"),
    ("Rumtek Monastery", 21, "temple", 7, "Largest monastery in Sikkim"),
    ("Elephant Falls", 22, "nature", 7, "Three-tiered waterfall near Shillong"),
    ("Jagannath Temple", 23, "temple", 9, "Sacred Hindu temple"),
    ("Puri Beach", 23, "beach", 7, "Pilgrimage beach town"),
    ("Sanchi Stupa", 24, "monument", 8, "Buddhist monument, UNESCO site"),
    ("Mehrangarh Fort", 25, "monument", 9, "Massive fort overlooking the Blue City"),
    ("Clock Tower Jodhpur", 25, "monument", 7, "Bustling market area"),
    ("Shaniwar Wada", 26, "monument", 7, "Fortification in the city of Pune"),
    ("Sabarmati Ashram", 27, "monument", 8, "Gandhi's historic ashram"),
    ("Pangong Lake", 28, "nature", 10, "Stunning high-altitude lake"),
    ("Magnetic Hill", 28, "nature", 7, "Optical illusion gravity hill"),
    ("Alleppey Backwaters", 29, "nature", 9, "Houseboat cruises through canals"),
    ("Western Temple Group", 30, "monument", 8, "Medieval Hindu and Jain temples"),
    ("Virupaksha Temple Hampi", 31, "temple", 8, "Ancient temple in ruins of Vijayanagara"),
    ("Ranthambore Fort", 32, "monument", 7, "Fort inside the tiger reserve"),
    ("Ranthambore Tiger Reserve", 32, "adventure", 9, "Top tiger safari destination"),
    ("Abbey Falls", 33, "nature", 7, "Waterfall amidst coffee plantations"),
    ("Radhanagar Beach", 34, "beach", 9, "Asia's best beach in Havelock"),
]

def seed_cities(cur):
    cur.executemany("INSERT INTO cities (name, state, lat, lng) VALUES (?,?,?,?)", CITIES)

def seed_attractions(cur):
    rows = []
    for name, ci, cat, pop, desc in ATTRACTIONS:
        city = CITIES[ci]
        rows.append((name, ci + 1, cat, pop, desc, city[2] + 0.01, city[3] + 0.01))
    cur.executemany(
        "INSERT INTO attractions (name, city_id, category, popularity, description, lat, lng) VALUES (?,?,?,?,?,?,?)",
        rows,
    )

def seed_transport(cur):
    """Generate transport options between nearby city pairs."""
    import math
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))

    rows = []
    for i, c1 in enumerate(CITIES):
        for j, c2 in enumerate(CITIES):
            if i == j:
                continue
            dist = haversine(c1[2], c1[3], c2[2], c2[3])
            if dist > 1500:
                continue
            # Car
            rows.append((i+1, j+1, "Car", int(dist * 8), round(dist / 60, 1)))
            # Bus
            rows.append((i+1, j+1, "Bus", int(dist * 3), round(dist / 45, 1)))
            # Train
            if dist > 50:
                rows.append((i+1, j+1, "Train", int(dist * 2), round(dist / 70, 1)))
            # Flight
            if dist > 400:
                rows.append((i+1, j+1, "Flight", int(1500 + dist * 3), round(dist / 700 + 1, 1)))
    cur.executemany(
        "INSERT INTO transport (from_city_id, to_city_id, mode, price_inr, duration_hrs) VALUES (?,?,?,?,?)",
        rows,
    )

def seed_stays(cur):
    """Generate hotel options for each city."""
    templates = [
        ("budget", ["Backpacker Hostel", "Budget Inn", "Guest House"], 500, 1500, 3.5),
        ("mid_range", ["Comfort Hotel", "Heritage Stay", "City Hotel"], 2000, 5000, 4.0),
        ("luxury", ["Grand Palace Hotel", "Luxury Resort", "Premium Suite"], 6000, 15000, 4.5),
    ]
    import random
    random.seed(42)
    rows = []
    for i, city in enumerate(CITIES):
        for typ, names, lo, hi, base_rating in templates:
            name = f"{random.choice(names)} {city[0]}"
            price = random.randint(lo, hi)
            rating = round(base_rating + random.uniform(-0.3, 0.5), 1)
            rows.append((i+1, name, typ, price, min(rating, 5.0)))
    cur.executemany(
        "INSERT INTO stays (city_id, name, type, price_per_night, rating) VALUES (?,?,?,?,?)",
        rows,
    )

def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    create_tables(cur)
    seed_cities(cur)
    seed_attractions(cur)
    seed_transport(cur)
    seed_stays(cur)
    conn.commit()
    # Print stats
    for table in ["cities", "attractions", "transport", "stays"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cur.fetchone()[0]} rows")
    conn.close()
    print(f"Database created at {DB_PATH}")

if __name__ == "__main__":
    main()
