from lib.ingredient import Ingredient

class IngredientRepository:

    def __init__(self, connection):
        self._connection = connection

    def all(self):
        rows = self._connection.execute('SELECT * FROM ingredients')
        ingredients = []
        for row in rows:
            item = Ingredient(row["id"], row["name"], row["category"])
            ingredients.append(item)
        return ingredients
    
    def find_ingredient(self, parameter, column):
        rows = self._connection.execute(f'SELECT * FROM ingredients WHERE {column} = %s', [parameter])
        if not rows:
            return None
        row = rows[0]
        return Ingredient(row["id"], row["name"], row["category"])