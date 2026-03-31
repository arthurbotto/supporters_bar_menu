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


class TestCreateRecipe:

    def test_returns_new_id(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        gin_id = seeded_db.execute("SELECT id FROM ingredients WHERE name = 'Gin'")[0]["id"]
        new_id = repo.create_recipe(negroni_id, gin_id, 10, 'ml', 10, False)
        assert isinstance(new_id, int)

    def test_recipe_item_appears_for_cocktail(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        mojito_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Mojito'")[0]["id"]
        mint_id = seeded_db.execute("SELECT id FROM ingredients WHERE name = 'Lime Juice'")[0]["id"]
        repo.create_recipe(mojito_id, mint_id, 5, 'leaves', 10, True)
        items = repo.for_cocktail(mojito_id)
        assert len(items) == 4


class TestUpdateRecipe:

    def test_amount_updated(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        gin_item = items[0]
        repo.update_recipe(gin_item.id, gin_item.ingredient_id, 45, gin_item.unit, gin_item.sort_order, gin_item.optional)
        updated_items = repo.for_cocktail(negroni_id)
        updated_gin = next(i for i in updated_items if i.id == gin_item.id)
        assert updated_gin.amount == 45

    def test_unit_updated(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        gin_item = items[0]
        repo.update_recipe(gin_item.id, gin_item.ingredient_id, gin_item.amount, 'dash', gin_item.sort_order, gin_item.optional)
        updated_items = repo.for_cocktail(negroni_id)
        updated_gin = next(i for i in updated_items if i.id == gin_item.id)
        assert updated_gin.unit == 'dash'


class TestDeleteRecipe:

    def test_item_gone_after_delete(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        gin_item_id = items[0].id
        repo.delete_recipe(gin_item_id)
        remaining = repo.for_cocktail(negroni_id)
        assert not any(i.id == gin_item_id for i in remaining)

    def test_other_items_unaffected(self, seeded_db):
        repo = RecipeItemRepository(seeded_db)
        negroni_id = seeded_db.execute("SELECT id FROM cocktails WHERE name = 'Negroni'")[0]["id"]
        items = repo.for_cocktail(negroni_id)
        repo.delete_recipe(items[0].id)
        remaining = repo.for_cocktail(negroni_id)
        assert len(remaining) == 2
        assert remaining[0].ingredient_name == 'Campari'
