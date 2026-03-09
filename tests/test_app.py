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