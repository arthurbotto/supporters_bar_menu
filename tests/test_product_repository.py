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
        assert len(wines) == 5
        assert [w.name for w in wines] == ['Malbec Reserva', 'No ABV Wine', 'Prosecco', 'Rioja Crianza', 'Sauvignon Blanc']

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
            'Mendoza', 2021, 'dry', 'full', 'medium', None
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
            None, None, None, None, None, None
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
        assert [h.name for h in hot] == ['English Breakfast Tea', 'Espresso']

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


# ===========================================================================
# Admin read methods
# ===========================================================================

class TestAllProductsForAdmin:

    def test_returns_all_products_including_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        products = repo.all_products_for_admin()
        names = [p.name for p in products]
        assert 'Delisted Bordeaux' in names
        assert 'Malbec Reserva' in names

    def test_returns_product_instances(self, seeded_db):
        repo = ProductRepository(seeded_db)
        products = repo.all_products_for_admin()
        assert all(isinstance(p, Product) for p in products)

    def test_ordered_by_category_then_name(self, seeded_db):
        repo = ProductRepository(seeded_db)
        products = repo.all_products_for_admin()
        # Within the beer category, Camden Hells should come before Guinness
        beer_names = [p.name for p in products if p.category == 'beer' and p.is_active]
        assert beer_names == sorted(beer_names)


class TestSearchProduct:

    def test_finds_by_partial_name(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_product('camden')
        assert len(results) == 1
        assert results[0].name == 'Camden Hells'

    def test_case_insensitive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_product('GUINNESS')
        assert len(results) == 1
        assert results[0].name == 'Guinness'

    def test_includes_inactive_products(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_product('delisted')
        assert len(results) > 0
        assert all('Delisted' in p.name for p in results)

    def test_returns_empty_for_no_match(self, seeded_db):
        repo = ProductRepository(seeded_db)
        assert repo.search_product('zzznomatch') == []

    def test_empty_query_returns_all(self, seeded_db):
        repo = ProductRepository(seeded_db)
        all_admin = repo.all_products_for_admin()
        search_all = repo.search_product('')
        assert len(search_all) == len(all_admin)

    def test_filter_by_category(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_product('', 'wine')
        assert all(p.category == 'wine' for p in results)
        assert any(p.name == 'Malbec Reserva' for p in results)
        assert not any(p.category == 'beer' for p in results)

    def test_combined_query_and_category(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_product('camden', 'beer')
        assert len(results) == 1
        assert results[0].name == 'Camden Hells'

    def test_category_filter_no_match(self, seeded_db):
        repo = ProductRepository(seeded_db)
        results = repo.search_product('camden', 'wine')
        assert results == []


class TestAllSnacks:

    def test_returns_all_snacks(self, seeded_db):
        repo = ProductRepository(seeded_db)
        snacks = repo.all_snacks()
        assert len(snacks) == 2

    def test_returns_snack_instances(self, seeded_db):
        repo = ProductRepository(seeded_db)
        snacks = repo.all_snacks()
        assert all(isinstance(s, Product) for s in snacks)

    def test_all_snacks_excludes_inactive(self, seeded_db):
        repo = ProductRepository(seeded_db)
        snacks = repo.all_snacks()
        assert all(s.is_active for s in snacks)
        assert not any(s.name == 'Nuts' for s in snacks)

    def test_vegan_snack_flagged(self, seeded_db):
        repo = ProductRepository(seeded_db)
        snacks = repo.all_snacks()
        crisps = next(s for s in snacks if s.name == 'Crisps')
        assert crisps.vegan is True

    def test_snack_with_description(self, seeded_db):
        repo = ProductRepository(seeded_db)
        snacks = repo.all_snacks()
        crisps = next(s for s in snacks if s.name == 'Crisps')
        assert crisps.description == 'Salted crisps'


# ===========================================================================
# Admin write methods
# ===========================================================================

class TestCreateProduct:

    def test_returns_new_id(self, seeded_db):
        repo = ProductRepository(seeded_db)
        new_id = repo.create_product('TEST-001', 'Test Beer', 'beer', None, None, None, 'England', 4.5, None, None, None)
        assert isinstance(new_id, int)

    def test_product_is_findable_after_creation(self, seeded_db):
        repo = ProductRepository(seeded_db)
        new_id = repo.create_product('TEST-001', 'Test Beer', 'beer', None, None, None, 'England', 4.5, None, None, None)
        found = repo.find(new_id)
        assert found is not None
        assert found.name == 'Test Beer'

    def test_created_product_has_correct_fields(self, seeded_db):
        repo = ProductRepository(seeded_db)
        new_id = repo.create_product('TEST-002', 'Test Gin', 'spirit', 'gin', 'A test gin', 'Test Co', 'Scotland', 41.0, None, None, None)
        found = repo.find(new_id)
        assert found.code == 'TEST-002'
        assert found.category == 'spirit'
        assert found.subcategory == 'gin'
        assert found.producer == 'Test Co'

    def test_new_product_is_active_by_default(self, seeded_db):
        repo = ProductRepository(seeded_db)
        new_id = repo.create_product('TEST-003', 'Active Product', 'beer', None, None, None, None, None, None, None, None)
        found = repo.find(new_id)
        assert found.is_active is True


class TestUpdateProduct:

    def test_name_is_updated(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beer = repo.find_by_code('BEER-001')
        repo.update_product(beer.id, 'Updated Hells', 'beer', None, None, 'Camden Town', 'England', 4.6, None, None, None)
        updated = repo.find(beer.id)
        assert updated.name == 'Updated Hells'

    def test_category_is_updated(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beer = repo.find_by_code('BEER-001')
        repo.update_product(beer.id, beer.name, 'soft', None, None, None, None, None, None, None, None)
        updated = repo.find(beer.id)
        assert updated.category == 'soft'

    def test_null_fields_accepted(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirit = repo.find_by_code('SPIRIT-001')
        repo.update_product(spirit.id, spirit.name, spirit.category, spirit.subcategory, None, None, None, None, None, None, None)
        updated = repo.find(spirit.id)
        assert updated.description is None
        assert updated.producer is None


class TestSetActive:

    def test_deactivates_active_product(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        repo.set_active(malbec.id, False)
        wines = repo.all_wines()
        assert not any(w.name == 'Malbec Reserva' for w in wines)

    def test_reactivates_inactive_product(self, seeded_db):
        repo = ProductRepository(seeded_db)
        delisted = repo.find_by_code('WINE-OFF')
        repo.set_active(delisted.id, True)
        wines = repo.all_wines()
        assert any(w.name == 'Delisted Bordeaux' for w in wines)


class TestDeleteProduct:

    def test_product_not_findable_after_deletion(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beer = repo.find_by_code('BEER-001')
        repo.delete_product(beer.id)
        assert repo.find(beer.id) is None

    def test_variants_cascade_deleted(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        assert len(repo.product_variants(malbec.id)) == 2
        repo.delete_product(malbec.id)
        assert repo.product_variants(malbec.id) == []

    def test_wine_details_cascade_deleted(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        repo.delete_product(malbec.id)
        assert repo.find_wine(malbec.id) is None


class TestUpsertWineDetails:

    def test_inserts_wine_details(self, seeded_db):
        repo = ProductRepository(seeded_db)
        new_id = repo.create_product('WINE-NEW', 'Chablis', 'wine', 'white', None, 'Brocard', 'France', 12.5, None, None, None)
        repo.upsert_wine_details(new_id, 'Chablis AOC', 2022, 'dry', 'light', 'high')
        found = repo.find_wine(new_id)
        assert found.region == 'Chablis AOC'
        assert found.vintage == 2022
        assert found.sweetness == 'dry'
        assert found.body == 'light'
        assert found.acidity == 'high'

    def test_updates_existing_wine_details(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        repo.upsert_wine_details(malbec.id, 'Luján de Cuyo', 2022, 'off-dry', 'full', 'low')
        updated = repo.find_wine(malbec.id)
        assert updated.region == 'Luján de Cuyo'
        assert updated.vintage == 2022
        assert updated.sweetness == 'off-dry'


class TestCreateVariant:

    def test_returns_new_id(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirit = repo.find_by_code('SPIRIT-001')
        new_id = repo.create_variant(spirit.id, 'Bottle', None, 39.00, 2)
        assert isinstance(new_id, int)

    def test_variant_appears_in_product_variants(self, seeded_db):
        repo = ProductRepository(seeded_db)
        spirit = repo.find_by_code('SPIRIT-001')
        repo.create_variant(spirit.id, 'Bottle', None, 39.00, 2)
        variants = repo.product_variants(spirit.id)
        assert len(variants) == 2
        labels = [v.serve_label for v in variants]
        assert 'Bottle' in labels

    def test_correct_fields(self, seeded_db):
        repo = ProductRepository(seeded_db)
        beer = repo.find_by_code('BEER-001')
        new_id = repo.create_variant(beer.id, 'Half', 284, 3.00, 2)
        variants = repo.product_variants(beer.id)
        half = next(v for v in variants if v.id == new_id)
        assert half.serve_label == 'Half'
        assert half.serve_ml == 284
        assert half.price == Decimal('3.00')
        assert half.sort_order == 2


class TestUpdateVariant:

    def test_price_is_updated(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        variant = repo.product_variants(malbec.id)[0]
        repo.update_variant(variant.id, variant.serve_label, variant.serve_ml, Decimal('7.50'), variant.sort_order)
        updated = repo.product_variants(malbec.id)
        changed = next(v for v in updated if v.id == variant.id)
        assert changed.price == Decimal('7.50')

    def test_serve_label_is_updated(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        variant = repo.product_variants(malbec.id)[0]
        repo.update_variant(variant.id, 'Small Glass', variant.serve_ml, variant.price, variant.sort_order)
        updated = repo.product_variants(malbec.id)
        changed = next(v for v in updated if v.id == variant.id)
        assert changed.serve_label == 'Small Glass'


class TestDeleteVariant:

    def test_variant_not_in_list_after_deletion(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        variant = repo.product_variants(malbec.id)[0]
        repo.delete_variant(variant.id)
        remaining = repo.product_variants(malbec.id)
        assert not any(v.id == variant.id for v in remaining)

    def test_other_variants_unaffected(self, seeded_db):
        repo = ProductRepository(seeded_db)
        malbec = repo.find_by_code('WINE-001')
        variants = repo.product_variants(malbec.id)
        assert len(variants) == 2
        repo.delete_variant(variants[0].id)
        remaining = repo.product_variants(malbec.id)
        assert len(remaining) == 1
        assert remaining[0].id == variants[1].id
