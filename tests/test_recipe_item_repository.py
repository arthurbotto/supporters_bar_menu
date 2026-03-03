import pytest
from lib.recipe_item_repository import RecipeItemRepository
from lib.recipe_item import RecipeItem


@pytest.fixture
def seeded_db(db_connection):
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_recipe_items.sql")
    return db_connection


class TestForCocktail:

    def test_returns_all_items_for_cocktail(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        print(items)
        assert len(items) == 3

    def test_returns_recipe_item_instances(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        assert all(isinstance(i, RecipeItem) for i in items)

    def test_returns_items_in_sort_order(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        assert [i.ingredient_name for i in items] == ['Gin', 'Campari', 'Sweet Vermouth']

    def test_returns_correct_fields(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        gin_item = items[0]
        assert gin_item == RecipeItem(
            gin_item.id,
            negroni_id,
            gin_item.ingredient_id,
            30, 'ml', 1, False,
            'Gin', 'spirit'
        )

    def test_returns_empty_list_for_unknown_cocktail(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        assert repo.for_cocktail(99999) == []

    def test_shared_ingredient_appears_in_multiple_cocktails(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        mojito_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Mojito'")[0]["id"]
        margarita_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Margarita'")[0]["id"]
        mojito_names = [i.ingredient_name for i in repo.for_cocktail(mojito_id)]
        margarita_names = [i.ingredient_name for i in repo.for_cocktail(margarita_id)]
        assert 'Lime Juice' in mojito_names
        assert 'Lime Juice' in margarita_names
