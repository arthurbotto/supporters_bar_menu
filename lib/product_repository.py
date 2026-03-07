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
            row.get("region"),
            row.get("vintage")
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
            """SELECT p.*, wd.region, wd.vintage
               FROM products p
               LEFT JOIN wine_details wd ON wd.product_id = p.id
               WHERE p.category = 'wine'
               ORDER BY p.name""")
        return [self._row_to_product(r) for r in rows]
    
    def all_spirits(self):
        rows = self._connection.execute(
            """SELECT p.*
               FROM products p
               WHERE p.category = 'spirit'
               ORDER BY p.subcategory""")
        return [self._row_to_product(r) for r in rows]

    def all_mocktails(self):
        rows = self._connection.execute(
            """SELECT p.*
               FROM products p
               WHERE p.category = 'mocktail'""")
        return [self._row_to_product(r) for r in rows]
    
    def all_beers(self):
        rows = self._connection.execute(
            "SELECT p.* FROM products p WHERE p.category = 'beer'"
        )
        return [self._row_to_product(r) for r in rows]
    
    def all_softs(self):
        rows = self._connection.execute(
            """SELECT p.*
               FROM products p
               WHERE p.category = 'soft'
               OR
               p.category = 'juice'
               ORDER BY p.id ASC"""
        )
        return [self._row_to_product(r) for r in rows]

    def all_hot_drinks(self):
        rows = self._connection.execute(
            "SELECT p.* FROM products p WHERE p.category = 'hot' ORDER BY p.id ASC"
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
            f"""SELECT p.*, wd.region, wd.vintage 
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
    
    def search_wine(self, query):
        query = query.strip()
        
        pattern_name = f"%{query}%"

        rows = self._connection.execute(
            """
            SELECT p.*, wd.region, wd.vintage
            FROM products p
            LEFT JOIN wine_details wd ON wd.product_id = p.id
            WHERE p.category = 'wine' AND p.name ILIKE %s
            ORDER BY p.name            
            """, [pattern_name])
        return [self._row_to_product(r) for r in rows]