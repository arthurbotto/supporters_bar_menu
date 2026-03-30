import pytest
from app import app as flask_app, server_error


class TestHomeRoute:
    def test_returns_200(self, web_client):
        response = web_client.get("/")
        assert response.status_code == 200
    
    def test_returns_category_links(self, web_client):
        response = web_client.get("/")
        assert b'Cocktails' in response.data
        assert b'Mocktails' in response.data
        assert b'Wines' in response.data
        assert b'Spirits' in response.data
        assert b'Beers' in response.data
        assert b'Soft Drinks' in response.data
        assert b'Hot Drinks' in response.data


class TestWineRoute:
    def test_returns_200(self, web_client):
        response = web_client.get("/wines")
        assert response.status_code == 200

class TestSearchWinesRoute:

    def test_returns_200(self, web_client, seeded_db_products):
        response = web_client.get("/search_wines")
        assert response.status_code == 200
    
    def test_returns_all_wines_with_no_query(self, web_client, seeded_db_products):
        response = web_client.get("/search_wines")
        assert b'Malbec Reserva' in response.data
        assert b'Prosecco' in response.data

    def test_filters_wines_by_search_query(self, web_client, seeded_db_products):
          response = web_client.get("/search_wines?q=malbec")
          assert b'Malbec Reserva' in response.data
          assert b'Prosecco' not in response.data

    def test_returns_no_results_message_when_no_match(self, web_client, seeded_db_products):
        response = web_client.get("/search_wines?q=zzznomatch")
        assert b'No wines found' in response.data

    def test_filters_wines_by_country(self, web_client, seeded_db_products):
        response = web_client.get("/search_wines?country=Argentina")
        assert b'Malbec Reserva' in response.data
        assert b'Prosecco' not in response.data

    def test_filters_wines_by_subcategory(self, web_client, seeded_db_products):
        response = web_client.get("/search_wines?subcategory=sparkling")
        assert b'Prosecco' in response.data
        assert b'Malbec Reserva' not in response.data

    def test_filters_wines_by_vegan(self, web_client, seeded_db_products):
        response = web_client.get("/search_wines?vegan=true")
        assert b'Malbec Reserva' in response.data
        assert b'Prosecco' in response.data
        assert b'Rioja Crianza' not in response.data

class TestWineModalRoute:

    def test_returns_200(self, web_client, seeded_db_products):
        response = web_client.get("/wines/1/modal")
        assert response.status_code == 200
    
    def test_returns_malbec(self, web_client, seeded_db_products):
        response = web_client.get("/wines/1/modal")
        assert b'Malbec Reserva' in response.data
    
    def test_returns_prosecco(self, web_client, seeded_db_products):
        response = web_client.get("/wines/4/modal")
        assert b'Prosecco' in response.data
    
    def test_returns_404_if_no_wine(self, web_client, seeded_db_products):
        response = web_client.get("/wines/10/modal")
        assert response.status_code == 404


class TestSpiritsRoute:

    def test_returns_200(self, web_client, seeded_db_products):
        response = web_client.get("/spirits")
        assert response.status_code == 200
    
    def test_returns_spirits(self, web_client, seeded_db_products):
        response = web_client.get("/spirits")
        assert b'Hendricks Gin' in response.data
        assert b'Grey Goose' in response.data


class TestCocktailsRoute:

    def test_returns_200(self, web_client, seeded_db_cocktails):
        response = web_client.get("/cocktails")
        assert response.status_code == 200

class TestSearchCocktailsRoute:

    def test_returns_200(self, web_client, seeded_db_cocktails):
        response = web_client.get("/search_cocktails")
        assert response.status_code == 200
    
    def test_returns_cocktails_with_no_query(self, web_client, seeded_db_cocktails):
        response = web_client.get("/search_cocktails")
        assert b'Negroni' in response.data
        assert b'Mojito' in response.data
        assert b'Margarita' in response.data
    
    def test_returns_by_cocktail_name_search(self, web_client, seeded_db_cocktails):
        response = web_client.get("/search_cocktails?q=negroni")
        assert b'Negroni' in response.data
        assert b'Mojito' not in response.data
    
    def test_returns_by_cocktail_ingredient_search(self, web_client, seeded_db_cocktails):
        response = web_client.get("/search_cocktails?q=rum")
        assert b'Negroni' not in response.data
        assert b'Mojito' in response.data
    
    def test_returns_multiple_cocktails_ingredient_search(self, web_client, seeded_db_cocktails):
        response = web_client.get("/search_cocktails?q=lime")
        assert b'Negroni' not in response.data
        assert b'Mojito' in response.data
        assert b'Margarita' in response.data
    
    def test_returns_no_results_message_when_no_match(self, web_client, seeded_db_cocktails):
        response = web_client.get("/search_cocktails?q=zzzznomatch")
        assert b'No cocktails found' in response.data

    def test_filters_cocktails_by_spirit_type(self, web_client, seeded_db_cocktails):
        response = web_client.get("/search_cocktails?spirit_type=gin")
        assert b'Negroni' in response.data
        assert b'Mojito' not in response.data

    def test_spirit_type_filter_with_empty_query(self, web_client, seeded_db_cocktails):
        # Regression: spirit_type must work when q is absent/empty
        response = web_client.get("/search_cocktails?spirit_type=rum")
        assert b'Mojito' in response.data
        assert b'Negroni' not in response.data

class TestCocktailModalRoute:

    def test_returns_200(self, web_client, seeded_db_cocktails):
        response = web_client.get("/cocktails/1/modal")
        assert response.status_code == 200
    
    def test_returns_negroni(self, web_client, seeded_db_cocktails):
        response = web_client.get("/cocktails/1/modal")
        assert b'Negroni' in response.data
    
    def test_returns_margarita(self, web_client, seeded_db_cocktails):
        response = web_client.get("/cocktails/3/modal")
        assert b'Margarita' in response.data
    
    def test_returns_404_if_no_cocktail(self, web_client, seeded_db_cocktails):
        response = web_client.get("/cocktails/10/modal")
        assert response.status_code == 404


class TestMocktailsRoute:

    def test_returns_200(self, web_client, seeded_db_products):
        response = web_client.get("/mocktails")
        assert response.status_code == 200

    def test_returns_mocktails(self, web_client, seeded_db_products):
        response = web_client.get("/mocktails")
        assert b'Virgin Mojito' in response.data
        assert b'Shirley Temple' in response.data


class TestBeersRoute:

    def test_returns_200(self, web_client, seeded_db_products):
        response = web_client.get("/beers")
        assert response.status_code == 200

    def test_returns_beers(self, web_client, seeded_db_products):
        response = web_client.get("/beers")
        assert b'Camden Hells' in response.data
        assert b'Guinness' in response.data


class TestSoftsRoute:

    def test_returns_200(self, web_client, seeded_db_products):
        response = web_client.get("/softs")
        assert response.status_code == 200

    def test_returns_soft_drinks(self, web_client, seeded_db_products):
        response = web_client.get("/softs")
        assert b'Coca-Cola' in response.data
        assert b'Orange Juice' in response.data


class TestHotDrinksRoute:

    def test_returns_200(self, web_client, seeded_db_products):
        response = web_client.get("/hot-drinks")
        assert response.status_code == 200

    def test_returns_hot_drinks(self, web_client, seeded_db_products):
        response = web_client.get("/hot-drinks")
        assert b'Espresso' in response.data
        assert b'English Breakfast Tea' in response.data


class TestErrorHandlers:

    def test_404_returns_not_found_page(self, web_client):
        response = web_client.get('/nonexistent-route')
        assert response.status_code == 404
        assert b'Page not found' in response.data

    def test_500_returns_error_page(self):
        with flask_app.test_request_context():
            html, status_code = server_error(Exception('test'))
        assert status_code == 500
        assert 'Something went wrong' in html


# ===========================================================================
# Admin routes
# ===========================================================================

class TestAdminAuth:

    def test_login_page_returns_200(self, web_client):
        response = web_client.get('/admin/login')
        assert response.status_code == 200

    def test_admin_dashboard_redirects_when_not_logged_in(self, web_client):
        response = web_client.get('/admin')
        assert response.status_code == 302

    def test_admin_products_redirects_when_not_logged_in(self, web_client):
        response = web_client.get('/admin/products')
        assert response.status_code == 302

    def test_admin_search_products_redirects_when_not_logged_in(self, web_client):
        response = web_client.get('/admin/search_products')
        assert response.status_code == 302


class TestAdminDashboard:

    def test_returns_200(self, admin_client):
        response = admin_client.get('/admin')
        assert response.status_code == 200


class TestAdminProductsRoute:

    def test_returns_200(self, admin_client):
        response = admin_client.get('/admin/products')
        assert response.status_code == 200

    def test_search_returns_all_products_with_no_query(self, admin_client, seeded_db_products):
        response = admin_client.get('/admin/search_products')
        assert b'Camden Hells' in response.data
        assert b'Delisted Lager' in response.data

    def test_search_includes_inactive_products(self, admin_client, seeded_db_products):
        response = admin_client.get('/admin/search_products?q=delisted')
        assert b'Delisted' in response.data

    def test_search_filters_by_name(self, admin_client, seeded_db_products):
        response = admin_client.get('/admin/search_products?q=camden')
        assert b'Camden Hells' in response.data
        assert b'Guinness' not in response.data


class TestAdminCocktailsRoute:

    def test_returns_200(self, admin_client):
        response = admin_client.get('/admin/cocktails')
        assert response.status_code == 200

    def test_search_returns_all_cocktails_with_no_query(self, admin_client, seeded_db_cocktails):
        response = admin_client.get('/admin/search_cocktails')
        assert b'Negroni' in response.data
        assert b'Mojito' in response.data
        assert b'Margarita' in response.data

    def test_search_filters_by_name(self, admin_client, seeded_db_cocktails):
        response = admin_client.get('/admin/search_cocktails?q=neg')
        assert b'Negroni' in response.data
        assert b'Mojito' not in response.data


class TestAdminToggleActive:

    def test_toggle_redirects_to_products(self, admin_client, seeded_db_products):
        response = admin_client.post('/admin/products/1/toggle')
        assert response.status_code == 302

    def test_toggle_deactivates_active_product(self, admin_client, seeded_db_products):
        admin_client.post('/admin/products/1/toggle')
        response = admin_client.get('/search_wines')
        assert b'Malbec Reserva' not in response.data


class TestAdminCreateProduct:

    def test_creates_product_and_redirects_to_variants(self, admin_client, seeded_db_products):
        response = admin_client.post('/admin/products/new', data={
            'name': 'Test Lager',
            'category': 'beer',
        })
        assert response.status_code == 302
        assert '/admin/products/' in response.headers['Location']
        assert 'variants' in response.headers['Location']

    def test_new_product_appears_in_admin_search(self, admin_client, seeded_db_products):
        admin_client.post('/admin/products/new', data={
            'name': 'Test Lager',
            'category': 'beer',
        })
        response = admin_client.get('/admin/search_products?q=Test+Lager')
        assert b'Test Lager' in response.data

    def test_creates_wine_with_details(self, admin_client, seeded_db_products):
        response = admin_client.post('/admin/products/new', data={
            'name': 'Test Burgundy',
            'category': 'wine',
            'subcategory': 'red',
            'region': 'Burgundy',
            'vintage': '2019',
            'sweetness': 'dry',
            'body': 'medium',
            'acidity': 'high',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Test Burgundy' in response.data


class TestAdminEditProduct:

    def test_edit_form_returns_200(self, admin_client, seeded_db_products):
        response = admin_client.get('/admin/products/1/edit')
        assert response.status_code == 200

    def test_edit_form_prepopulates_product_name(self, admin_client, seeded_db_products):
        response = admin_client.get('/admin/products/1/edit')
        assert b'Malbec Reserva' in response.data

    def test_update_redirects_to_products(self, admin_client, seeded_db_products):
        response = admin_client.post('/admin/products/1/edit', data={
            'name': 'Renamed Malbec',
            'category': 'wine',
            'subcategory': 'red',
        })
        assert response.status_code == 302
        assert '/admin/products' in response.headers['Location']

    def test_updated_name_appears_in_search(self, admin_client, seeded_db_products):
        admin_client.post('/admin/products/1/edit', data={
            'name': 'Renamed Malbec',
            'category': 'wine',
            'subcategory': 'red',
        })
        response = admin_client.get('/admin/search_products?q=Renamed+Malbec')
        assert b'Renamed Malbec' in response.data


class TestAdminDeleteProduct:

    def test_delete_redirects_to_products(self, admin_client, seeded_db_products):
        response = admin_client.post('/admin/products/1/delete')
        assert response.status_code == 302

    def test_deleted_product_not_in_search(self, admin_client, seeded_db_products):
        admin_client.post('/admin/products/1/delete')
        response = admin_client.get('/admin/search_products?q=Malbec')
        assert b'Malbec Reserva' not in response.data


class TestAdminVariants:

    def test_variants_page_returns_200(self, admin_client, seeded_db_products):
        response = admin_client.get('/admin/products/1/variants')
        assert response.status_code == 200

    def test_create_variant_redirects(self, admin_client, seeded_db_products):
        response = admin_client.post('/admin/products/1/variants/new', data={
            'serve_label': 'Bottle',
            'price': '39.00',
            'sort_order': '3',
        })
        assert response.status_code == 302

    def test_created_variant_appears_on_variants_page(self, admin_client, seeded_db_products):
        admin_client.post('/admin/products/1/variants/new', data={
            'serve_label': 'Bottle',
            'price': '39.00',
            'sort_order': '3',
        })
        response = admin_client.get('/admin/products/1/variants')
        assert b'Bottle' in response.data

    def test_update_variant_redirects(self, admin_client, seeded_db_products):
        # Variant id=1 belongs to Malbec (first INSERT in test_products.sql)
        response = admin_client.post('/admin/variants/1/edit', data={
            'product_id': '1',
            'serve_label': '125ml',
            'price': '7.00',
            'sort_order': '1',
        })
        assert response.status_code == 302

    def test_delete_variant_redirects(self, admin_client, seeded_db_products):
        response = admin_client.post('/admin/variants/1/delete', data={
            'product_id': '1',
        })
        assert response.status_code == 302

    def test_deleted_variant_not_on_variants_page(self, admin_client, seeded_db_products):
        # Malbec has 2 variants (125ml and 175ml). Delete the first.
        admin_client.post('/admin/variants/1/delete', data={'product_id': '1'})
        response = admin_client.get('/admin/products/1/variants')
        # After deletion, only 175ml remains — 125ml label should be absent
        assert response.data.count(b'125ml') == 0