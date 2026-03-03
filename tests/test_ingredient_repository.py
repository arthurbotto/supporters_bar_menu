import pytest
from lib.ingredient import Ingredient
from lib.ingredient_repository import IngredientRepository


@pytest.fixture
def seeded_db(db_connection):
    # schema.sql drops and recreates all tables, giving a clean slate with correct types.
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_ingredients.sql")
    return db_connection

class TestAllIngredients:

    def test_returns_all_ingredients(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredients = repo.all()
        assert len(ingredients) == 8
        assert [i.name for i in ingredients] == [
            'Gin',          
            'Campari',      
            'Sweet Vermouth',
            'White Rum',    
            'Lime Juice',   
            'Sugar Syrup',  
            'Tequila',      
            'Triple Sec',]
    
    def test_returns_ingredient_instances(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredients = repo.all()
        assert all(isinstance(i, Ingredient) for i in ingredients)
    
    def test_returns_correct_fields(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredients = repo.all()
        gin = next(i for i in ingredients if i.name == 'Gin')

        assert gin == Ingredient(
            gin.id, 'Gin', 'spirit'
        )
    
    def test_returns_empty_list_when_no_ingredients(self, db_connection):
        db_connection.seed("seeds/schema.sql")
        repo = IngredientRepository(db_connection)
        assert repo.all() == []

class TestFindIngredient:

    def test_return_ingredient_by_id(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredient = repo.find_ingredient(2, 'id')
        assert ingredient.name == 'Campari'
        assert ingredient.category == 'liqueur'
    
    def test_return_ingredient_by_name(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredient = repo.find_ingredient('Campari', 'name')
        assert ingredient.name == 'Campari'
        assert ingredient.category == 'liqueur'
    
    def test_return_none_for_missing_id(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        assert repo.find_ingredient(99999, 'id') is None
    
    def test_return_none_for_missing_name(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        assert repo.find_ingredient('car', 'name') is None

