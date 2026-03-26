from lib.product import Product
from lib.product_variant import ProductVariant

class ProductRepository:
    def __init__(self, connection):
        self._connection = connection

    # -------------------------
    # Private helpers
    # -------------------------

    def _row_to_product(self, row):
        return Product(
            row["id"],
            row["code"],
            row["name"],
            row["category"],
            row["subcategory"],
            row["description"],
            row["producer"],
            row["country"],
            row["abv"],
            row["vegan"],
            row["organic"],
            row["is_active"],
            row.get("region"),
            row.get("vintage"),
            row.get("sweetness"),
            row.get("body"),
            row.get("acidity")
        )
    
    def _row_to_variants(self, row):
        return ProductVariant(
            row["id"],
            row["product_id"],
            row["serve_label"],
            row["serve_ml"],
            row["price"],
            row["sort_order"]
        )

    def _normalize_query(self, q):
        return (q or "").strip()
    
    # -------------------------------

    
    def all_wines(self):
        rows = self._connection.execute(
            """SELECT p.*, wd.region, wd.vintage, wd.sweetness, wd.body, wd.acidity
               FROM products p
               LEFT JOIN wine_details wd ON wd.product_id = p.id
               WHERE p.category = 'wine' AND p.is_active = TRUE
               ORDER BY p.name""")
        return [self._row_to_product(r) for r in rows]
    
    def all_spirits(self):
        rows = self._connection.execute(
            """SELECT p.*
               FROM products p
               WHERE p.category = 'spirit' AND p.is_active = TRUE
               ORDER BY p.subcategory""")
        return [self._row_to_product(r) for r in rows]

    def all_mocktails(self):
        rows = self._connection.execute(
            """SELECT p.*
               FROM products p
               WHERE p.category = 'mocktail' AND p.is_active = TRUE""")
        return [self._row_to_product(r) for r in rows]
    
    def all_beers(self):
        rows = self._connection.execute(
            "SELECT p.* FROM products p WHERE p.category = 'beer' AND p.is_active = TRUE"
        )
        return [self._row_to_product(r) for r in rows]
    
    def all_softs(self):
        rows = self._connection.execute(
            """SELECT p.*
               FROM products p
               WHERE p.category = 'soft' AND p.is_active = TRUE
               ORDER BY p.id ASC"""
        )
        return [self._row_to_product(r) for r in rows]

    def all_hot_drinks(self):
        rows = self._connection.execute(
            "SELECT p.* FROM products p WHERE p.category = 'hot' AND p.is_active = TRUE ORDER BY p.id ASC"
        )
        return [self._row_to_product(r) for r in rows]

        
    
    def product_variants(self, product_id):
        rows = self._connection.execute(
            """
            SELECT 
                v.id, 
                v.product_id,
                v.serve_label,
                v.serve_ml,
                v.price,
                v.sort_order
            FROM product_variants v
            WHERE v.product_id = %s
            ORDER BY v.sort_order;
            """,
            [product_id])
        
        variants = [self._row_to_variants(r) for r in rows]

        return variants


    def find(self, product_id):
        rows = self._connection.execute(
            "SELECT * FROM products WHERE id = %s",
            [product_id]
        )
        if len(rows) == 0:
            return None
        return self._row_to_product(rows[0])
    
    def find_wine(self, wine_id):
        rows = self._connection.execute(
            f"""SELECT p.*, wd.region, wd.vintage, wd.sweetness, wd.body, wd.acidity 
            FROM products p 
            LEFT JOIN wine_details wd ON wd.product_id = p.id
            WHERE p.id = %s AND p.category = 'wine'""",
            [wine_id]
        )
        if len(rows) == 0:
            return None
        return self._row_to_product(rows[0])

    def find_by_code(self, code):
        rows = self._connection.execute(
            "SELECT * FROM products WHERE code = %s",
            [code]
        )
        if len(rows) == 0:
            return None
        return self._row_to_product(rows[0])
    
    def wine_countries(self) -> list[str]:
        rows = self._connection.execute(
            """SELECT DISTINCT country FROM products
                WHERE category = 'wine' AND is_active = TRUE AND country IS NOT NULL
                ORDER BY country"""
        )
        return [row["country"] for row in rows]
    
    def wine_producer(self) -> list[str]:
        rows = self._connection.execute(
            """SELECT DISTINCT producer FROM products
                WHERE category = 'wine' AND is_active = TRUE AND producer IS NOT NULL
                ORDER BY producer"""
        )
        return [row["producer"] for row in rows]

    def search_product(self, query=''):
        q = f"%{query.strip()}%"

        rows = self._connection.execute(
            """
            SELECT p.*
            FROM products p
            WHERE p.name ILIKE %s
            ORDER BY p.name
        """, [q])

        return [self._row_to_product(r) for r in rows]


    
    def search_wine(self, query='', country='', subcategory='', producer='', sweetness='', body='', acidity='', organic=None, vegan=None):
        conditions = ["p.category = 'wine'", "p.is_active = TRUE"]
        params = []

        if query:
            conditions.append("p.name ILIKE %s")
            params.append(f"%{query.strip()}%")
        if country:
            conditions.append("p.country = %s")
            params.append(country)
        if subcategory:
            conditions.append("p.subcategory = %s")
            params.append(subcategory)
        if producer:
            conditions.append("p.producer = %s")
            params.append(producer)
        if sweetness:
            conditions.append("wd.sweetness = %s")
            params.append(sweetness)
        if body:
            conditions.append("wd.body = %s")
            params.append(body)
        if acidity:
            conditions.append("wd.acidity = %s")
            params.append(acidity)            
        if organic is not None:
            conditions.append("p.organic = %s")
            params.append(organic)
        if vegan is not None:
            conditions.append("p.vegan = %s")
            params.append(vegan)

        rows = self._connection.execute(
            f"""
            SELECT p.*, wd.region, wd.vintage, wd.sweetness, wd.body, wd.acidity
            FROM products p
            LEFT JOIN wine_details wd ON wd.product_id = p.id
            WHERE {" AND ".join(conditions)}
            ORDER BY p.name
            """, params)
        return [self._row_to_product(r) for r in rows]

    # -------------------------
    # Admin write methods
    # -------------------------

    def all_products_for_admin(self):
        rows = self._connection.execute(
            "SELECT * FROM products ORDER BY category, name"
        )
        return [self._row_to_product(r) for r in rows]

    def create_product(self, code, name, category, subcategory, description, producer, country, abv, vegan, organic):
        rows = self._connection.execute(
            """INSERT INTO products (code, name, category, subcategory, description, producer, country, abv, vegan, organic)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            [code, name, category, subcategory, description, producer, country, abv, vegan, organic]
        )
        return rows[0]["id"]

    def update_product(self, product_id, name, category, subcategory, description, producer, country, abv, vegan, organic):
        self._connection.execute(
            """UPDATE products SET name=%s, category=%s, subcategory=%s, description=%s,
               producer=%s, country=%s, abv=%s, vegan=%s, organic=%s WHERE id=%s""",
            [name, category, subcategory, description, producer, country, abv, vegan, organic, product_id]
        )

    def set_active(self, product_id, is_active):
        self._connection.execute(
            "UPDATE products SET is_active=%s WHERE id=%s",
            [is_active, product_id]
        )

    def delete_product(self, product_id):
        self._connection.execute(
            "DELETE FROM products WHERE id=%s",
            [product_id]
        )

    def upsert_wine_details(self, product_id, region, vintage, sweetness, body, acidity):
        self._connection.execute(
            """INSERT INTO wine_details (product_id, region, vintage, sweetness, body, acidity)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (product_id) DO UPDATE
               SET region=EXCLUDED.region, vintage=EXCLUDED.vintage,
                   sweetness=EXCLUDED.sweetness, body=EXCLUDED.body, acidity=EXCLUDED.acidity""",
            [product_id, region, vintage, sweetness, body, acidity]
        )

    def create_variant(self, product_id, serve_label, serve_ml, price, sort_order):
        rows = self._connection.execute(
            """INSERT INTO product_variants (product_id, serve_label, serve_ml, price, sort_order)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            [product_id, serve_label, serve_ml, price, sort_order]
        )
        return rows[0]["id"]

    def update_variant(self, variant_id, serve_label, serve_ml, price, sort_order):
        self._connection.execute(
            """UPDATE product_variants SET serve_label=%s, serve_ml=%s, price=%s, sort_order=%s
               WHERE id=%s""",
            [serve_label, serve_ml, price, sort_order, variant_id]
        )

    def delete_variant(self, variant_id):
        self._connection.execute(
            "DELETE FROM product_variants WHERE id=%s",
            [variant_id]
        )