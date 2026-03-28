import pytest
from decimal import Decimal
from lib.product_repository import ProductRepository
from lib.product import Product
from lib.product_variant import ProductVariant


@pytest.fixture
def seeded_db(db_connection):
    # schema.sql drops and recreates all tables, giving a clean slate with correct types.
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_products.sql")
    return db_connection


class TestAllWines:

    def test_returns_all_wines(self, seeded_db):
        repo = ProductRepository(seeded_db)
        wines = repo.all_wines()
        assert len(wines) == 4
        assert [w.name for w in wines] == ['Malbec Reserva', 'Prosecco', 'Rioja Crianza', 'Sauvignon Blanc']

    def test_returns_wine_instances(self, seeded_db):
        repo = ProductRepository(seeded_db)
        wines = repo.all_wines()
        assert all(isinstance(w, Product) for w in wines)

    def test_returns_correct_fields(self, seeded_db):
        repo = ProductRepository(seeded_db)
        wines = repo.all_wines()
        malbec = next(w for w in wines if w.name == 'Malbec Reserva')
        assert malbec == Product(
            malbec.id, 'WINE-001', 'Malbec Reserva', 'wine', 'red',
            'Plum and spice', 'Catena', 'Argentina', Decimal('13.5'), True, None, True,
            'Mendoza', 2021, 'dry', 'full', 'medium'
        )

    def test_wine_with_null_vintage(self, seeded_db):
        repo = ProductRepository(seeded_db)
        wines = repo.all_wines()
        prosecco = next(w for w in wines if w.name == 'Prosecco')
        assert prosecco.region == 'Veneto'
        assert prosecco.vintage is None

    def test_returns_empty_list_when_no_wines(self, db_connection):
        db_connection.seed("seeds/schema.sql")
        repo = ProductRepository(db_connection)
        assert repo.all_wines() == []

    def test_all_wines_excludes_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        wines = repo.all_wines()
        assert all(w.is_active for w in wines)
        assert not any(w.name == 'Delisted Bordeaux' for w in wines)

class TestAllSpirits:

    def test_returns_all_spirits(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirits = repo.all_spirits()
        assert len(spirits) == 2
        assert [s.name for s in spirits] == ['Hendricks Gin', 'Grey Goose']

    def test_returns_spirit_instances(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirits = repo.all_spirits()
        assert all(isinstance(s, Product) for s in spirits)

    def test_returns_correct_fields(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirits = repo.all_spirits()
        hendricks = next(s for s in spirits if s.name == 'Hendricks Gin')
        assert hendricks == Product(
            hendricks.id, 'SPIRIT-001', 'Hendricks Gin', 'spirit', 'gin',
            None, "Hendrick's", 'Scotland', Decimal('41.4'), None, None, True,
            None, None, None, None, None
        )
    
    def test_all_spirits_excludes_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirits = repo.all_spirits()
        assert all(s.is_active for s in spirits)
        assert not any(s.name == 'Delisted Rum' for s in spirits)


class TestAllBeers:

    def test_returns_all_beers(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beers = repo.all_beers()
        assert len(beers) == 2

    def test_returns_beer_instances(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beers = repo.all_beers()
        assert all(isinstance(b, Product) for b in beers)

    def test_beers_have_null_subcategory(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beers = repo.all_beers()
        assert all(b.subcategory is None for b in beers)
    
    def test_all_beers_excludes_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beers = repo.all_beers()
        assert all(b.is_active for b in beers)
        assert not any(s.name == 'Delisted Lager' for s in beers)


class TestAllSofts:

    def test_returns_all_softs(self, seeded_db):
        repo = ProductRepository(seeded_db)
        softs = repo.all_softs()
        assert len(softs) == 2
        assert [s.name for s in softs] == ['Coca-Cola', 'Orange Juice']
    
    def test_all_spirits_excludes_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        softs = repo.all_softs()
        assert all(s.is_active for s in softs)
        assert not any(s.name == 'Delisted Lemonade' for s in softs)


class TestAllHotDrinks:

    def test_returns_all_hot_drinks(self, seeded_db):
        repo = ProductRepository(seeded_db)
        hot = repo.all_hot_drinks()
        assert len(hot) == 2
        assert [h.name for h in hot] == ['Espresso', 'English Breakfast Tea']

    def test_returns_hot_drink_instances(self, seeded_db):
        repo = ProductRepository(seeded_db)
        hot = repo.all_hot_drinks()
        assert all(isinstance(h, Product) for h in hot)

    def test_all_hot_drinks_excludes_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        hot_drinks = repo.all_hot_drinks()
        assert all(h.is_active for h in hot_drinks)
        assert not any(s.name == 'Delisted Green Tea' for s in hot_drinks)


class TestAllMocktails:

    def test_returns_all_mocktails(self, seeded_db):
        repo = ProductRepository(seeded_db)
        mocktails = repo.all_mocktails()
        assert len(mocktails) == 2
        assert {m.name for m in mocktails} == {'Virgin Mojito', 'Shirley Temple'}

    def test_mocktails_have_zero_abv(self, seeded_db):
        repo = ProductRepository(seeded_db)
        mocktails = repo.all_mocktails()
        assert all(m.abv == Decimal('0') for m in mocktails)
    
    def test_all_mocktails_excludes_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        mocktails = repo.all_mocktails()
        assert all(m.is_active for m in mocktails)
        assert not any(m.name == 'Delisted Mocktail' for m in mocktails)


class TestProductVariants:

    def test_returns_variants_for_product(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        variants = repo.product_variants(malbec.id)
        assert len(variants) == 2

    def test_returns_variants_in_sort_order(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        variants = repo.product_variants(malbec.id)
        assert [v.serve_label for v in variants] == ['125ml', '175ml']

    def test_returns_correct_variant_fields(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        variants = repo.product_variants(malbec.id)
        v = variants[0]
        assert v.serve_label == '125ml'
        assert v.serve_ml == 125
        assert v.price == Decimal('6.50')
        assert v.sort_order == 1

    def test_returns_empty_list_for_unknown_product(self, seeded_db):
        repo = ProductRepository(seeded_db)
        assert repo.product_variants(99999) == []


class TestFind:

    def test_returns_product_by_id(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirit = repo.find_by_code('SPIRIT-001')
        found = repo.find(spirit.id)
        assert found.code == 'SPIRIT-001'
        assert found.name == 'Hendricks Gin'

    def test_find_does_not_include_wine_details(self, seeded_db):
        repo = ProductRepository(seeded_db)
        wine = repo.find_by_code('WINE-001')
        found = repo.find(wine.id)
        assert found.region is None
        assert found.vintage is None

    def test_returns_none_for_missing_id(self, seeded_db):
        repo = ProductRepository(seeded_db)
        assert repo.find(99999) is None


class TestFindWine:

    def test_finds_wine_by_id(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        found = repo.find_wine(malbec.id)
        assert found.name == 'Malbec Reserva'
        assert found.region == 'Mendoza'
        assert found.vintage == 2021


    def test_returns_none_for_missing_wine(self, seeded_db):
        repo = ProductRepository(seeded_db)
        assert repo.find_wine(99999) is None


class TestFindByCode:

    def test_returns_product_by_code(self, seeded_db):
        repo = ProductRepository(seeded_db)
        product = repo.find_by_code('BEER-001')
        assert product.name == 'Camden Hells'
        assert product.category == 'beer'

    def test_returns_none_for_missing_code(self, seeded_db):
        repo = ProductRepository(seeded_db)
        assert repo.find_by_code('NOPE-999') is None


class TestSearchWine:

    def test_returns_matching_wines(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine('rioja')
        assert len(results) == 1
        assert results[0].name == 'Rioja Crianza'

    def test_returns_empty_list_for_no_match(self, seeded_db):
        repo = ProductRepository(seeded_db)
        assert repo.search_wine('zzznomatch') == []

    def test_search_is_case_insensitive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine('PROSECCO')
        assert len(results) == 1
        assert results[0].name == 'Prosecco'

    def test_partial_match(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine('blanc')
        assert len(results) == 1
        assert results[0].name == 'Sauvignon Blanc'

    def test_filter_by_country(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine(country='Argentina')
        assert len(results) == 1
        assert results[0].name == 'Malbec Reserva'

    def test_filter_by_subcategory(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine(subcategory='sparkling')
        assert len(results) == 1
        assert results[0].name == 'Prosecco'

    def test_filter_by_vegan(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine(vegan=True)
        assert {w.name for w in results} == {'Malbec Reserva', 'Prosecco'}

    def test_filter_by_sweetness(self, seeded_db):
        # Prosecco is off-dry; the three reds/white are dry
        repo = ProductRepository(seeded_db)
        results = repo.search_wine(sweetness='off-dry')
        assert len(results) == 1
        assert results[0].name == 'Prosecco'

    def test_filter_by_body(self, seeded_db):
        # Malbec is full-bodied
        repo = ProductRepository(seeded_db)
        results = repo.search_wine(body='full')
        assert len(results) == 1
        assert results[0].name == 'Malbec Reserva'

    def test_filter_by_acidity(self, seeded_db):
        # Sauvignon Blanc has high acidity; others are medium
        repo = ProductRepository(seeded_db)
        results = repo.search_wine(acidity='high')
        assert len(results) == 1
        assert results[0].name == 'Sauvignon Blanc'

    def test_combined_query_and_country_filter(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine(query='malbec', country='Argentina')
        assert len(results) == 1
        assert results[0].name == 'Malbec Reserva'

    def test_combined_filters_no_match(self, seeded_db):
        repo = ProductRepository(seeded_db)
        assert repo.search_wine(country='Argentina', subcategory='white') == []

    def test_excludes_inactive_wines(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_wine()
        assert not any(w.name == 'Delisted Bordeaux' for w in results)


class TestWineCountries:

    def test_returns_distinct_active_countries(self, seeded_db):
        repo = ProductRepository(seeded_db)
        countries = repo.wine_countries()
        assert set(countries) == {'Argentina', 'Italy', 'New Zealand', 'Spain'}

    def test_returns_alphabetically_sorted(self, seeded_db):
        repo = ProductRepository(seeded_db)
        countries = repo.wine_countries()
        assert countries == sorted(countries)

    def test_excludes_inactive_wine_country(self, seeded_db):
        # Delisted Bordeaux is France (inactive) — must not appear
        repo = ProductRepository(seeded_db)
        assert 'France' not in repo.wine_countries()


class TestWineProducer:

    def test_returns_distinct_active_producers(self, seeded_db):
        repo = ProductRepository(seeded_db)
        producers = repo.wine_producer()
        assert set(producers) == {'Bisol', 'Catena', 'Featherdrop', 'Muga'}

    def test_returns_alphabetically_sorted(self, seeded_db):
        repo = ProductRepository(seeded_db)
        producers = repo.wine_producer()
        assert producers == sorted(producers)
