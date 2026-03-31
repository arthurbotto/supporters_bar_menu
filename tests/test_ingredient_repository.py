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
            gin.id, 'Gin', 'spirit', 'gin'
        )
    
    def test_returns_empty_list_when_no_ingredients(self, db_connection):
        db_connection.seed("seeds/schema.sql")
        repo = IngredientRepository(db_connection)
        assert repo.all() == []

class TestFindIngredient:

    def test_return_ingredient_by_id(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredient = repo.find_ingredient(2)
        assert ingredient.name == 'Campari'
        assert ingredient.category == 'liqueur'

    def test_return_none_for_missing_id(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        assert repo.find_ingredient(99999) is None


class TestSpiritTypes:

    def test_returns_only_spirit_subcategories(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        types = repo.spirit_types()
        assert set(types) == {'gin', 'rum', 'tequila'}

    def test_returns_alphabetically_sorted(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        types = repo.spirit_types()
        assert types == sorted(types)

    def test_excludes_non_spirit_subcategories(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        types = repo.spirit_types()
        assert 'aperitivo' not in types
        assert 'sweet' not in types
        assert 'orange_liqueur' not in types

    def test_returns_empty_list_when_no_spirits(self, db_connection):
        db_connection.seed("seeds/schema.sql")
        repo = IngredientRepository(db_connection)
        assert repo.spirit_types() == []


class TestFindIngredientByName:

    def test_finds_by_name(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredient = repo.find_ingredient_by_name('Gin')
        assert ingredient is not None
        assert ingredient.name == 'Gin'

    def test_case_insensitive(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        ingredient = repo.find_ingredient_by_name('GIN')
        assert ingredient is not None
        assert ingredient.name == 'Gin'

    def test_returns_none_for_missing(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        assert repo.find_ingredient_by_name('Absinthe') is None


class TestCreateIngredient:

    def test_returns_new_id(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        new_id = repo.create_ingredient('Elderflower Cordial', 'cordial', None)
        assert isinstance(new_id, int)

    def test_ingredient_findable_after_create(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        new_id = repo.create_ingredient('Elderflower Cordial', 'cordial', None)
        found = repo.find_ingredient(new_id)
        assert found is not None
        assert found.name == 'Elderflower Cordial'
        assert found.category == 'cordial'


class TestUpdateIngredient:

    def test_name_updated(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        gin = repo.find_ingredient_by_name('Gin')
        repo.update_ingredient(gin.id, 'London Dry Gin', 'spirit', 'gin')
        updated = repo.find_ingredient(gin.id)
        assert updated.name == 'London Dry Gin'

    def test_category_updated(self, seeded_db):
        repo = IngredientRepository(seeded_db)
        campari = repo.find_ingredient_by_name('Campari')
        repo.update_ingredient(campari.id, campari.name, 'spirit', 'bitter')
        updated = repo.find_ingredient(campari.id)
        assert updated.category == 'spirit'
        assert updated.subcategory == 'bitter'

