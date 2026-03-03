import pytest
from decimal import Decimal
from lib.cocktail_repository import CocktailRepository
from lib.cocktail import Cocktail


@pytest.fixture
def seeded_db(db_connection):
    # schema.sql drops and recreates all tables, giving a clean slate with correct types.
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_cocktails.sql")
    return db_connection


# ===========================================================================
# all()
# ===========================================================================

class TestAll:

    def test_returns_all_cocktails(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        cocktails = repo.all()
        assert len(cocktails) == 3
        assert {c.name for c in cocktails} == {"Negroni", "Mojito", "Margarita"}

    def test_returns_cocktail_instances(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        cocktails = repo.all()
        assert all(isinstance(c, Cocktail) for c in cocktails)

    def test_returns_correct_fields(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        cocktails = repo.all()
        negroni = next(c for c in cocktails if c.name == "Negroni")
        assert negroni == Cocktail(
            1, "Negroni", "Bitter Italian classic", "Invented in Florence",
            "Stirred", "Rocks", "Orange peel", Decimal("24"), Decimal("9.50"),
        )

    def test_returns_empty_list_when_no_cocktails(self, db_connection):
        db_connection.seed("seeds/schema.sql")
        repo = CocktailRepository(db_connection)
        assert repo.all() == []


# ===========================================================================
# find_cocktail()
# ===========================================================================

class TestFindCocktail:

    def test_find_by_id(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        cocktail = repo.find_cocktail(1, "id")
        assert cocktail.name == "Negroni"
        assert cocktail.method == "Stirred"
        assert cocktail.glass == "Rocks"

    def test_find_by_name(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        cocktail = repo.find_cocktail("Mojito", "name")
        assert cocktail.id == 2
        assert cocktail.name == "Mojito"

    def test_returns_cocktail_instance(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        assert isinstance(repo.find_cocktail(1, "id"), Cocktail)

    def test_returns_none_when_id_not_found(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        assert repo.find_cocktail(999, "id") is None

    def test_returns_none_when_name_not_found(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        assert repo.find_cocktail("Nonexistent", "name") is None


# ===========================================================================
# search()
# ===========================================================================

class TestSearch:

    def test_search_by_full_cocktail_name(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("Negroni")
        assert len(results) == 1
        assert results[0].name == "Negroni"

    def test_search_is_case_insensitive_for_name(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("negroni")
        assert len(results) == 1
        assert results[0].name == "Negroni"

    def test_search_by_partial_name(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("Mar")
        assert len(results) == 1
        assert results[0].name == "Margarita"

    def test_search_by_ingredient_name(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("Tequila")
        assert len(results) == 1
        assert results[0].name == "Margarita"

    def test_search_ingredient_is_case_insensitive(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("tequila")
        assert len(results) == 1
        assert results[0].name == "Margarita"

    def test_search_returns_multiple_results(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        # Lime Juice is shared between Mojito and Margarita
        results = repo.search_cocktail("Lime")
        assert {c.name for c in results} == {"Mojito", "Margarita"}

    def test_search_multiple_results_ordered_alphabetically(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        # Both match via ingredient (same rank), so result order is alphabetical
        results = repo.search_cocktail("Lime")
        assert results[0].name == "Margarita"
        assert results[1].name == "Mojito"

    def test_search_returns_cocktail_instances(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("Negroni")
        assert all(isinstance(c, Cocktail) for c in results)

    def test_search_returns_empty_list_for_no_match(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        assert repo.search_cocktail("zzz") == []

    def test_search_strips_surrounding_whitespace(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("  Negroni  ")
        assert len(results) == 1
        assert results[0].name == "Negroni"

    def test_search_ingredient_respects_word_boundary(self, seeded_db):
        repo = CocktailRepository(seeded_db)
        # 'rum' matches 'White Rum' at a word boundary (space before 'Rum').
        # No other ingredient or cocktail name contains 'rum', so only Mojito is returned.
        results = repo.search_cocktail("rum")
        assert len(results) == 1
        assert results[0].name == "Mojito"

    def test_search_name_match_ranked_above_ingredient_match(self, seeded_db):
        # Insert a cocktail whose name contains 'gin' (no ingredients needed).
        # Searching 'gin' should return it (rank 0, name match)
        # before Negroni (rank 1, ingredient match on 'Gin').
        seeded_db.execute(
            "INSERT INTO cocktails (name, description, history, method, glass, garnish, abv, price) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            ["Gin Fizz", "A classic highball", "British origin", "Built", "Highball", "Lemon wheel", 10, 7.50],
        )
        repo = CocktailRepository(seeded_db)
        results = repo.search_cocktail("gin")
        assert results[0].name == "Gin Fizz"
        assert results[1].name == "Negroni"
