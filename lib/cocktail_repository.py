import re
from lib.cocktail import Cocktail

class CocktailRepository:

    def __init__(self, connection):
        self._connection = connection

    def all(self):
        rows = self._connection.execute('SELECT * FROM cocktails ORDER BY ID ASC')
        
    
    def find_cocktail(self, parameter, column):
        rows = self._connection.execute(f'SELECT * FROM cocktails WHERE {column} = %s', [parameter])
        if not rows:
            return None
        row = rows[0]
        return Cocktail(row["id"], row["name"], row["subcategory"], row["description"], row["history"], row["method"], row["glass"], row["garnish"], row["abv"], row["price"])
    
    def search_cocktail(self, query):
        query = query.strip()
        pattern_name = f"%{query}%"
        pattern_ing = rf"(^|\s){re.escape(query)}"
        rows = self._connection.execute(
        """
        SELECT DISTINCT c.*,
          CASE
            WHEN c.name ILIKE %s THEN 0
            WHEN i.name ~* %s THEN 1
            ELSE 2
          END AS rank
        FROM cocktails c 
        LEFT JOIN recipe_items r ON r.cocktail_id = c.id
        LEFT JOIN ingredients i ON i.id = r.ingredient_id
        WHERE c.name ILIKE %s OR i.name ~* %s
        ORDER BY rank, c.name
        """,
        [pattern_name, pattern_ing, pattern_name, pattern_ing]
    )
        cocktails = []
        for row in rows:
            item = Cocktail(row["id"], row["name"],row["subcategory"], row["description"], row["history"], row["method"], row["glass"], row["garnish"], row["abv"], row["price"])
            cocktails.append(item)
        return cocktails
    

    