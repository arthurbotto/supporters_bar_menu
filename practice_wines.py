# Standalone practice file to visualize the wines grouping logic

# --- Simplified Product class (same structure as lib/product.py) ---
class Product:
    def __init__(self, id, name, subcategory, producer, country, region, vintage):
        self.id = id
        self.name = name
        self.subcategory = subcategory
        self.producer = producer
        self.country = country
        self.region = region
        self.vintage = vintage

    def __repr__(self):
        return f"Product({self.id}, {self.name}, {self.subcategory}, {self.producer}, {self.country}, {self.region}, {self.vintage})"


# --- Simplified ProductVariant class (same structure as lib/product_variant.py) ---
class ProductVariant:
    def __init__(self, id, product_id, serve_label, serve_ml, price, sort_order):
        self.id = id
        self.product_id = product_id
        self.serve_label = serve_label
        self.serve_ml = serve_ml
        self.price = price
        self.sort_order = sort_order

    def __repr__(self):
        return f"ProductVariant(product_id={self.product_id}, {self.serve_label}, {self.serve_ml}ml, £{self.price})"


# --- Fake data simulating what product_repo.all_wines() returns ---
# This is a list of Product objects, just like the real database query would return
wines = [
    Product(1, "Malbec Reserva",     "red",      "Bodega Norton",    "Argentina",    "Mendoza",     2020),
    Product(2, "Chianti Classico",   "red",      "Antinori",         "Italy",        "Tuscany",     2019),
    Product(3, "Pinot Grigio",       "white",    "Santa Margherita", "Italy",        "Alto Adige",  2022),
    Product(4, "Sauvignon Blanc",    "white",    "Cloudy Bay",       "New Zealand",  "Marlborough", 2021),
    Product(5, "Chardonnay",         "white",    "Kumeu River",      "New Zealand",  "Kumeu",       2020),
    Product(6, "Whispering Angel",   "rose",     "Caves d'Esclans",  "France",       "Provence",    2022),
    Product(7, "Prosecco Superiore", "sparkling","Bisol",            "Italy",        "Veneto",      2021),
    Product(8, "Champagne Brut",     "sparkling","Moet & Chandon",   "France",       "Champagne",   2018),
    Product(9, "Sauternes",          "dessert",  "Chateau d'Yquem",  "France",       "Bordeaux",    2017),
]

# --- Fake data simulating what product_repo.product_variants(wine.id) returns ---
# In the real app, this is fetched from DB per wine. Here we store them in a dict keyed by product_id.
fake_variants = {
    1: [  # Malbec Reserva — more expensive red
        ProductVariant(101, 1, "125ml",  125, 6.50, 1),
        ProductVariant(102, 1, "175ml",  175, 8.50, 2),
        ProductVariant(103, 1, "500ml",  500, 22.00, 3),
    ],
    2: [  # Chianti Classico — cheaper red (should sort BEFORE Malbec)
        ProductVariant(104, 2, "125ml",  125, 5.50, 1),
        ProductVariant(105, 2, "175ml",  175, 7.50, 2),
        ProductVariant(106, 2, "500ml",  500, 20.00, 3),
    ],
    3: [  # Pinot Grigio — cheapest white
        ProductVariant(107, 3, "125ml",  125, 5.00, 1),
        ProductVariant(108, 3, "175ml",  175, 7.00, 2),
        ProductVariant(109, 3, "500ml",  500, 19.00, 3),
    ],
    4: [  # Sauvignon Blanc — mid white
        ProductVariant(110, 4, "125ml",  125, 6.00, 1),
        ProductVariant(111, 4, "175ml",  175, 8.00, 2),
        ProductVariant(112, 4, "500ml",  500, 21.00, 3),
    ],
    5: [  # Chardonnay — most expensive white
        ProductVariant(113, 5, "125ml",  125, 7.00, 1),
        ProductVariant(114, 5, "175ml",  175, 9.50, 2),
        ProductVariant(115, 5, "500ml",  500, 25.00, 3),
    ],
    6: [  # Whispering Angel — bottle only
        ProductVariant(116, 6, "500ml",  500, 35.00, 1),
    ],
    7: [  # Prosecco — glass and bottle
        ProductVariant(117, 7, "125ml",  125, 7.00, 1),
        ProductVariant(118, 7, "500ml",  500, 28.00, 2),
    ],
    8: [  # Champagne — glass and bottle (more expensive sparkling)
        ProductVariant(119, 8, "125ml",  125, 12.00, 1),
        ProductVariant(120, 8, "500ml",  500, 48.00, 2),
    ],
    9: [  # Sauternes — small pour only
        ProductVariant(121, 9, "75ml",   75,  9.00, 1),
    ],
}


# --- Step 1: See what wines looks like (the raw list) ---
print("=" * 60)
print("STEP 1: wines (the raw list from all_wines())")
print("=" * 60)
print(f"Type: {type(wines)}")
print(f"Length: {len(wines)}")
print()
for wine in wines:
    print(f"  {wine}")
print()


# --- Step 2: Group wines, attach variants, and build section_sizes in one pass ---
grouped = {}
section_sizes = {}

for wine in wines:
    wine.variants = fake_variants[wine.id]
    wine.price_by_ml = {v.serve_ml: v.price for v in wine.variants}
    if wine.subcategory not in grouped:
        grouped[wine.subcategory] = []
        section_sizes[wine.subcategory] = set()
    grouped[wine.subcategory].append(wine)
    for ml in wine.price_by_ml:
        section_sizes[wine.subcategory].add(ml)

section_sizes = {k: sorted(v) for k, v in section_sizes.items()}

print("=" * 60)
print("STEP 2: grouped + section_sizes (single pass)")
print("=" * 60)
for subcategory, wine_list in grouped.items():
    print(f"  '{subcategory}' -> {[w.name for w in wine_list]}")
    print(f"    sizes: {section_sizes[subcategory]}")
print()


# --- Step 3: sort() with lambda ---
# lambda w: min(w.price_by_ml.values())
# For each wine w, this extracts the cheapest price across all serve sizes.
# sort() compares those numbers to rank wines within each section.

print("=" * 60)
print("STEP 3: Showing what the lambda extracts from each wine (reds)")
print("=" * 60)
for wine in grouped['red']:
    sort_value = min(wine.price_by_ml.values())
    print(f"  {wine.name}")
    print(f"    price_by_ml = {wine.price_by_ml}")
    print(f"    min(values) = {sort_value}  <-- this is what sort() compares")
print()

print("=" * 60)
print("STEP 3b: Reds BEFORE sort")
print("=" * 60)
print([w.name for w in grouped['red']])
print()

for wines_list in grouped.values():
    wines_list.sort(key=lambda w: min(w.price_by_ml.values()))

print("=" * 60)
print("STEP 3c: Reds AFTER sort (cheapest first)")
print("=" * 60)
print([w.name for w in grouped['red']])
print()


# --- Step 4: section_order controls display order ---
section_order = ['red', 'white', 'rose', 'sparkling', 'dessert']

print("=" * 60)
print("STEP 4: Final output — each section sorted by price, low to high")
print("=" * 60)
for section in section_order:
    wine_list = grouped.get(section, [])
    print(f"\n  --- {section.upper()} ({len(wine_list)} wines) ---")
    for wine in wine_list:
        cheapest = min(wine.price_by_ml.values())
        print(f"    {wine.name:25} cheapest serve: £{cheapest:.2f}")


for section, wines in grouped.items():
    print(f"\nSECTION: {section}")
    print(f"type(wines): {type(wines)}")
    for wine in wines:
        print(f"  {wine.name} -> {wine.price_by_ml}")
