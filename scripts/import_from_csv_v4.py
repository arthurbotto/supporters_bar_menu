# scripts/import_from_csv_v4.py
#
# - products_base.csv (shared fields + OPTIONAL product_code)
# - wine_details.csv  (wine-only: region, vintage) keyed by product_code
# - product_variants.csv (product_code, serve_label, serve_ml, price, sort_order)
# Cocktails / ingredients / recipe_items stay the same.
# - If products_base.csv row has no product_code, auto-generate one using slugify()
#   based on category + name (+ producer if present).
# - print the generated codes at the end so I can copy/paste them into
#   wine_details.csv and product_variants.csv if needed.
#
# NOTE:
# wine_details.csv and product_variants.csv still require product_code because those
# CSVs don't have enough fields to generate it reliably.

import os
import csv
import re
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


# ---------------------------
# 1) Database connection
# ---------------------------

_db_url = os.getenv('DATABASE_URL')
if not _db_url:
    raise Exception(
        "DATABASE_URL is not set. Create a .env file with DATABASE_URL=... (and make sure .env is in .gitignore)."
    )
DB_DSN = f"{_db_url}/supporters_bar_menu"

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


# ---------------------------
# 2) Helpers
# ---------------------------

def read_csv(filename):
    """Read CSV from /data using UTF-8 (supports Excel BOM). Returns list[dict]."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def to_int(value):
    v = (value or "").strip()
    if v == "":
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def to_decimal(value):
    v = (value or "").strip()
    if v == "":
        return None
    try:
        return Decimal(v)
    except Exception:
        return None


def to_bool(value):
    v = (value or "").strip().lower()
    if v == "":
        return None
    if v in ("true", "t", "1", "yes", "y"):
        return True
    if v in ("false", "f", "0", "no", "n"):
        return False
    return None


def fetch_one_or_none(cur):
    """Safe fetchone: returns None when the SELECT has 0 rows.

    Some psycopg binary builds can raise InterfaceError on fetchone() when the
    result set is empty. We treat that case as 'no row'.
    """
    try:
        return cur.fetchone()
    except psycopg.InterfaceError as e:
        msg = str(e).lower()
        if "row must be included" in msg or "no result set" in msg:
            return None
        raise



def slugify(value):
    """
    Turn text into a safe ID like: "Chapel Down Rosé Brut" -> "chapel_down_rose_brut"
    - lowercase
    - replace non [a-z0-9] with underscores
    - collapse multiple underscores
    """
    v = (value or "").strip().lower()
    v = re.sub(r"[^a-z0-9]+", "_", v)
    v = re.sub(r"_+", "_", v).strip("_")
    return v or "item"


def make_product_code(category, name, producer=None):
    """
    Auto-generate a product_code when it's missing in products_base.csv.

    IMPORTANT: products_base.csv doesnt have vintage, so I cant include vintage here.
    If I ever stock the same wine with multiple vintages, I should manually set
    product_code to include the year (e.g. wine_cloudy_bay_2023 vs wine_cloudy_bay_2024).
    """
    parts = [category or "", name or ""]
    if producer:
        parts.append(producer)
    return slugify("_".join(parts))


# ---------------------------
# 3) Upsert helpers
# (Upsert = insert if missing, else update)
# ---------------------------

def upsert_cocktail(cur, row):
    """
    cocktails.csv columns:
    name,description,history,method,glass,garnish,abv,price
    """
    name = row["name"].strip()

    cur.execute("SELECT id FROM cocktails WHERE name = %s LIMIT 1", [name])
    existing = fetch_one_or_none(cur)

    description = (row.get("description") or "").strip() or None
    history = (row.get("history") or "").strip() or None
    method = (row.get("method") or "").strip() or None
    glass = (row.get("glass") or "").strip() or None
    garnish = (row.get("garnish") or "").strip() or None
    abv = to_decimal(row.get("abv"))
    price = to_decimal(row.get("price"))

    if existing is None:
        cur.execute(
            """
            INSERT INTO cocktails (name, description, history, method, glass, garnish, abv, price)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            [name, description, history, method, glass, garnish, abv, price],
        )
        return cur.fetchone()["id"]

    cocktail_id = existing["id"]
    cur.execute(
        """
        UPDATE cocktails
        SET description=%s, history=%s, method=%s, glass=%s, garnish=%s, abv=%s, price=%s
        WHERE id=%s
        """,
        [description, history, method, glass, garnish, abv, price, cocktail_id],
    )
    return cocktail_id


def upsert_ingredient(cur, row):
    """
    ingredients.csv columns:
    name,category
    """
    name = row["name"].strip()

    cur.execute("SELECT id FROM ingredients WHERE name=%s LIMIT 1", [name])
    existing = fetch_one_or_none(cur)

    category = (row.get("category") or "").strip().lower() or None

    if existing is None:
        cur.execute(
            "INSERT INTO ingredients (name, category) VALUES (%s,%s) RETURNING id",
            [name, category],
        )
        return cur.fetchone()["id"]

    ingredient_id = existing["id"]
    cur.execute("UPDATE ingredients SET category=%s WHERE id=%s", [category, ingredient_id])
    return ingredient_id


def import_recipe_items(cur, rows):
    """
    recipe_items.csv columns
    cocktail_name,ingredient_name,amount,unit,sort_order,optional
    """
    # wipe + rebuild
    cur.execute("DELETE FROM recipe_items")

    for row in rows:
        cocktail_name = (row.get("cocktail_name") or "").strip()
        ingredient_name = (row.get("ingredient_name") or "").strip()
        if cocktail_name == "" or ingredient_name == "":
            continue

        cur.execute("SELECT id FROM cocktails WHERE name=%s", [cocktail_name])
        c = fetch_one_or_none(cur)
        if c is None:
            raise ValueError(f"Missing cocktail for recipe_items: {cocktail_name}")
        cocktail_id = c["id"]

        cur.execute("SELECT id FROM ingredients WHERE name=%s LIMIT 1", [ingredient_name])
        i = fetch_one_or_none(cur)
        if i is None:
            raise ValueError(f"Missing ingredient for recipe_items: {ingredient_name}")
        ingredient_id = i["id"]

        amount = to_decimal(row.get("amount"))
        unit = (row.get("unit") or "").strip() or None
        sort_order = to_int(row.get("sort_order")) or 1
        optional = to_bool(row.get("optional"))
        if optional is None:
            optional = False

        cur.execute(
            """
            INSERT INTO recipe_items
              (cocktail_id, ingredient_id, amount, unit, sort_order, optional)
            VALUES
              (%s,%s,%s,%s,%s,%s)
            """,
            [cocktail_id, ingredient_id, amount, unit, sort_order, optional],
        )


def upsert_menu_section(cur, row):
    """
    menu_sections.csv columns:
    name,sort_order
    """
    name = row["name"].strip()
    sort_order = to_int(row.get("sort_order")) or 1

    cur.execute("SELECT id FROM menu_sections WHERE name=%s LIMIT 1", [name])
    existing = fetch_one_or_none(cur)

    if existing is None:
        cur.execute(
            "INSERT INTO menu_sections (name, sort_order) VALUES (%s,%s) RETURNING id",
            [name, sort_order],
        )
        return cur.fetchone()["id"]

    section_id = existing["id"]
    cur.execute("UPDATE menu_sections SET sort_order=%s WHERE id=%s", [sort_order, section_id])
    return section_id


def find_section_id(cur, section_name):
    section_name = (section_name or "").strip()
    if section_name == "":
        return None

    cur.execute("SELECT id FROM menu_sections WHERE name=%s LIMIT 1", [section_name])
    row = fetch_one_or_none(cur)
    if row is None:
        raise ValueError(f"Missing menu_sections row for name: {section_name}")
    return row["id"]


def upsert_product_base(cur, row, generated_codes_out):
    """
    products_base.csv columns:
    product_code (optional), name, category, subcategory, section_name, description, abv, vegan, organic, producer, country
    """
    name = (row.get("name") or "").strip()
    category = (row.get("category") or "").strip().lower()
    producer = (row.get("producer") or "").strip() or None

    code = (row.get("product_code") or "").strip()
    if code == "":
        code = make_product_code(category, name, producer)
        generated_codes_out.append({
            "name": name,
            "category": category,
            "producer": producer or "",
            "product_code": code
        })

    subcategory = (row.get("subcategory") or "").strip().lower() or None
    section_id = find_section_id(cur, row.get("section_name"))
    description = (row.get("description") or "").strip() or None
    country = (row.get("country") or "").strip() or None

    abv = to_decimal(row.get("abv"))
    vegan = to_bool(row.get("vegan"))
    organic = to_bool(row.get("organic"))

    cur.execute("SELECT id FROM products WHERE code=%s LIMIT 1", [code])
    existing = fetch_one_or_none(cur)

    if existing is None:
        cur.execute(
            """
            INSERT INTO products
              (section_id, code, name, category, subcategory, description, producer, country, abv, vegan, organic)
            VALUES
              (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            [section_id, code, name, category, subcategory, description,
             producer, country, abv, vegan, organic],
        )
        return cur.fetchone()["id"]

    product_id = existing["id"]
    cur.execute(
        """
        UPDATE products
        SET section_id=%s, name=%s, category=%s, subcategory=%s, description=%s,
            producer=%s, country=%s, abv=%s, vegan=%s, organic=%s
        WHERE id=%s
        """,
        [section_id, name, category, subcategory, description,
         producer, country, abv, vegan, organic, product_id],
    )
    return product_id


def find_product_id_by_code(cur, product_code):
    code = (product_code or "").strip()
    if code == "":
        raise ValueError("Missing product_code")
    cur.execute("SELECT id FROM products WHERE code=%s LIMIT 1", [code])
    row = fetch_one_or_none(cur)
    if row is None:
        raise ValueError(f"Missing products row for code: {code}")
    return row["id"]


def upsert_wine_detail(cur, row):
    """
    wine_details.csv columns:
    product_code,region,vintage
    """
    code = (row.get("product_code") or "").strip()
    if code == "":
        raise ValueError(
            "wine_details.csv row missing product_code. "
            "Add the code (or add the product in products_base.csv and rerun to see the generated code)."
        )

    product_id = find_product_id_by_code(cur, code)

    region = (row.get("region") or "").strip() or None
    vintage = to_int(row.get("vintage"))

    cur.execute("SELECT product_id FROM wine_details WHERE product_id=%s", [product_id])
    existing = fetch_one_or_none(cur)

    if existing is None:
        cur.execute(
            "INSERT INTO wine_details (product_id, region, vintage) VALUES (%s,%s,%s)",
            [product_id, region, vintage],
        )
        return

    cur.execute(
        "UPDATE wine_details SET region=%s, vintage=%s WHERE product_id=%s",
        [region, vintage, product_id],
    )


def upsert_product_variant(cur, row):
    """
    product_variants.csv
    product_code,serve_label,serve_ml,price,sort_order
    """
    product_code = (row.get("product_code") or "").strip()
    serve_label = (row.get("serve_label") or "").strip()

    if product_code == "" or serve_label == "":
        raise ValueError(
            "product_variants.csv row missing product_code or serve_label. "
            "Add product_code (or add the product in products_base.csv and rerun to see the generated code)."
        )

    product_id = find_product_id_by_code(cur, product_code)

    serve_ml = to_int(row.get("serve_ml"))
    price = to_decimal(row.get("price"))
    sort_order = to_int(row.get("sort_order")) or 1

    # Upsert by unique (product_id, serve_label, serve_ml)
    if serve_ml is None:
        cur.execute(
            """
            SELECT id FROM product_variants
            WHERE product_id=%s AND serve_label=%s AND serve_ml IS NULL
            """,
            [product_id, serve_label],
        )
    else:
        cur.execute(
            """
            SELECT id FROM product_variants
            WHERE product_id=%s AND serve_label=%s AND serve_ml=%s
            """,
            [product_id, serve_label, serve_ml],
        )

    existing = fetch_one_or_none(cur)

    if existing is None:
        cur.execute(
            """
            INSERT INTO product_variants
              (product_id, serve_label, serve_ml, price, sort_order)
            VALUES
              (%s,%s,%s,%s,%s)
            """,
            [product_id, serve_label, serve_ml, price, sort_order],
        )
        return

    variant_id = existing["id"]
    cur.execute(
        """
        UPDATE product_variants
        SET price=%s, sort_order=%s
        WHERE id=%s
        """,
        [price, sort_order, variant_id],
    )


# ---------------------------
# 4) Main import flow
# ---------------------------

def main():
    # Load CSVs
    cocktails = read_csv("cocktails.csv")
    ingredients = read_csv("ingredients.csv")
    recipe_items = read_csv("recipe_items.csv")

    sections = read_csv("menu_sections.csv")
    products_base = read_csv("products_base.csv")
    wine_details = read_csv("wine_details.csv")
    variants = read_csv("product_variants.csv")

    generated_codes = []  # list of dicts (printed at the end)

    with psycopg.connect(DB_DSN, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # A) Cocktails
            print("Importing cocktails...")
            for row in cocktails:
                if not row.get("name"):
                    continue
                upsert_cocktail(cur, row)

            # B) Ingredients
            print("Importing ingredients...")
            for row in ingredients:
                if not row.get("name"):
                    continue
                upsert_ingredient(cur, row)

            # C) Recipe items (depends on both cocktails + ingredients)
            print("Importing recipe items (refreshing recipes)...")
            import_recipe_items(cur, recipe_items)

            # D) Menu sections
            print("Importing menu sections...")
            for row in sections:
                if not row.get("name"):
                    continue
                upsert_menu_section(cur, row)

            # E) Products base
            print("Importing products (base)...")
            for row in products_base:
                if not (row.get("name") and row.get("category")):
                    continue
                upsert_product_base(cur, row, generated_codes)

            # F) Wine details
            print("Importing wine details...")
            for row in wine_details:
                if not row.get("product_code"):
                    continue
                upsert_wine_detail(cur, row)

            # G) Product variants
            print("Importing product variants...")
            for row in variants:
                if not (row.get("product_code") and row.get("serve_label")):
                    continue
                upsert_product_variant(cur, row)

        conn.commit()

    print("✅ Import complete!")

    if generated_codes:
        print("\n⚠️ Generated product_code for rows missing it in products_base.csv:")
        for g in generated_codes:
            producer = f" | producer={g['producer']}" if g["producer"] else ""
            print(f"- {g['category']} | {g['name']}{producer} -> {g['product_code']}")
        print("\nCopy those codes into wine_details.csv / product_variants.csv for new items.")


if __name__ == "__main__":
    main()
