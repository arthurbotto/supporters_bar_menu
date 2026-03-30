import re
from lib.cocktail import Cocktail

class CocktailRepository:

    def __init__(self, connection):
        self._connection = connection
    
    # -------------------------
    # Private helpers
    # -------------------------

    def _row_to_cocktail(self, row):
        return Cocktail(
            row["id"],
            row["name"],
            row["subcategory"],
            row["description"],
            row["history"],
            row["method"],
            row["glass"],
            row["garnish"],
            row["abv"],
            row["price"],
            row["is_active"],
            row["image_url"]
        )

    def all(self):
        rows = self._connection.execute('SELECT * FROM cocktails WHERE is_active = TRUE ORDER BY ID ASC')
        return [self._row_to_cocktail(r) for r in rows]
    
    def find_cocktail(self, cocktail_id):
        rows = self._connection.execute(
            'SELECT * FROM cocktails WHERE id = %s',
            [cocktail_id]
        )
        if not rows:
            return None
        return self._row_to_cocktail(rows[0])
    
    def search_cocktail(self, query='', spirit_type=''):
        query = query.strip()
        spirit_type = spirit_type.strip()

        conditions = ["c.is_active = TRUE"]
        where_params = []

        pattern_name = f"%{query}%"
        # \m = word start boundary, \M = word end boundary (PostgreSQL regex)
        # This ensures "gin" matches "Gin Tanqueray" but not "Ginger Beer"
        # re.escape() makes special characters like + or . safe to use in regex
        pattern_ing = rf"\m{re.escape(query)}\M" if query else ""

        if query:
            conditions.append("(c.name ILIKE %s OR i.name ~* %s OR i.subcategory ILIKE %s)")
            where_params.extend([pattern_name, pattern_ing, pattern_name])

        if spirit_type:
            conditions.append("i.subcategory = %s")
            where_params.append(spirit_type)

        where = "WHERE " + " AND ".join(conditions)

        if query:
            rank_sql = "CASE WHEN c.name ILIKE %s THEN 0 WHEN i.name ~* %s THEN 1 ELSE 2 END AS rank"
            rank_params = [pattern_name, pattern_ing]
        else:
            rank_sql = "0 AS rank"
            rank_params = []

        rows = self._connection.execute(
            f"""
            SELECT DISTINCT c.*, {rank_sql}
            FROM cocktails c
            LEFT JOIN recipe_items r ON r.cocktail_id = c.id
            LEFT JOIN ingredients i ON i.id = r.ingredient_id
            {where}
            ORDER BY rank, c.name
            """,
            rank_params + where_params
        )
        return [self._row_to_cocktail(r) for r in rows]

    
    # -------------------------
    # Admin write methods
    # -------------------------


    def all_cocktails_for_admin(self):
        rows = self._connection.execute(
            "SELECT * FROM cocktails ORDER BY subcategory, name"
        )
        return [self._row_to_cocktail(r) for r in rows]
    
    def search_cocktail_admin(self, query=''):
        q = f"%{query.strip()}%"

        rows = self._connection.execute(
            """
            SELECT *
            FROM cocktails
            WHERE name ILIKE %s
            ORDER BY subcategory, name
        """, [q])

        return [self._row_to_cocktail(r) for r in rows]
    
    def create_cocktail(self, name, subcategory, description, history, method, glass, garnish, abv, price, image_url):
        rows = self._connection.execute(
            """INSERT INTO cocktails (name, subcategory, description, history, method, glass, garnish, abv, price, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            [name, subcategory, description, history, method, glass, garnish, abv, price, image_url]
        )
        return rows[0]["id"]
    
    def update_cocktail(self, cocktail_id, name, subcategory, description, history, method, glass, garnish, abv, price, image_url):
        self._connection.execute(
            """UPDATE cocktails SET name=%s, subcategory=%s, description=%s, history=%s,
                 method=%s, glass=%s, garnish=%s, abv=%s, price=%s, image_url=%s WHERE id=%s""",
                   [name, subcategory, description, history, method, glass, garnish, abv, price, image_url, cocktail_id]
        )

    def set_active(self, cocktail_id, is_active):
        self._connection.execute(
            "UPDATE cocktails SET is_active=%s WHERE id=%s",
            [is_active, cocktail_id]
        )

    def delete_cocktail(self, cocktail_id):
        self._connection.execute(
            "DELETE FROM cocktails WHERE id=%s",
            [cocktail_id]
        )
    


    