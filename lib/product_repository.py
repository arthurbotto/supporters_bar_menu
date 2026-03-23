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
            row["section_id"],
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