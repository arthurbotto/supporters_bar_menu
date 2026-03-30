from lib.ingredient import Ingredient

class IngredientRepository:

    def __init__(self, connection):
        self._connection = connection

    def all(self):
        rows = self._connection.execute('SELECT * FROM ingredients')
        ingredients = []
        for row in rows:
            item = Ingredient(row["id"], row["name"], row["category"], row["subcategory"])
            ingredients.append(item)
        return ingredients
    
    def find_ingredient(self, ingredient_id):
        rows = self._connection.execute("SELECT * FROM ingredients WHERE id=%s", [ingredient_id])
        if not rows:
            return None
        row = rows[0]
        return Ingredient(row["id"], row["name"], row["category"], row["subcategory"])
    
    def find_ingredient_by_name(self, ingredient_name):
        rows = self._connection.execute("SELECT * FROM ingredients WHERE name ILIKE %s", [ingredient_name])
        if not rows:
            return None
        row = rows[0]
        return Ingredient(row["id"], row["name"], row["category"], row["subcategory"])
    
    def spirit_types(self) -> list[str]:
        rows = self._connection.execute(
            """SELECT DISTINCT subcategory FROM ingredients
                WHERE subcategory IS NOT NULL AND category = 'spirit'
                 ORDER BY subcategory"""
        )
        return [row["subcategory"] for row in rows]
    
    def create_ingredient(self, name, category, subcategory):
        rows = self._connection.execute(
            """INSERT INTO ingredients (name, category, subcategory)
                VALUES (%s, %s, %s) RETURNING id""",
                [name, category, subcategory]
        )
        return rows[0]["id"]

    def update_ingredient(self, ingredient_id, name, category, subcategory):
        self._connection.execute(
            """UPDATE ingredients SET name=%s, category=%s, subcategory=%s WHERE id=%s""",
                [name, category, subcategory, ingredient_id]
        ) 