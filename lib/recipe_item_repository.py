from lib.recipe_item import RecipeItem

class RecipeItemRepository:
    def __init__(self, connection):
        self._connection = connection

    def for_cocktail(self, cocktail_id):
        rows = self._connection.execute(
            """
            SELECT
                r.id,
                r.cocktail_id,
                r.ingredient_id,
                r.amount,
                r.unit,
                r.sort_order,
                r.optional,
                i.name AS ingredient_name,
                i.category AS ingredient_category,
                i.subcategory AS ingredient_subcategory
            FROM recipe_items r
            JOIN ingredients i ON r.ingredient_id = i.id
            WHERE r.cocktail_id = %s
            ORDER BY r.sort_order;
            """,
            [cocktail_id])
    
        items = []
        for row in rows:
            item = RecipeItem(
                row["id"],
                row["cocktail_id"],
                row["ingredient_id"],
                row["amount"],
                row["unit"],
                row["sort_order"],
                row["optional"],
                row["ingredient_name"],
                row["ingredient_category"],
                row["ingredient_subcategory"],
            )
            items.append(item)
        return items
    
    def create_recipe(self, cocktail_id, ingredient_id, amount, unit, sort_order, optional):
        rows = self._connection.execute(
            """INSERT INTO recipe_items (cocktail_id, ingredient_id, amount, unit, sort_order, optional)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                [cocktail_id, ingredient_id, amount, unit, sort_order, optional]
        )
        return rows[0]["id"]
    
    def update_recipe(self, recipe_id, ingredient_id, amount, unit, sort_order, optional):
        self._connection.execute(
            """UPDATE recipe_items SET ingredient_id=%s, amount=%s, unit=%s, sort_order=%s, optional=%s
                WHERE id=%s""",
                [ingredient_id, amount, unit, sort_order, optional, recipe_id]
        )
    
    def delete_recipe(self, recipe_id):
        self._connection.execute(
            "DELETE FROM recipe_items WHERE id=%s", [recipe_id]
        )