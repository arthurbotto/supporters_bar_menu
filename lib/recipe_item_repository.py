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
                i.category AS ingredient_category
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
            )
            items.append(item)
        return items