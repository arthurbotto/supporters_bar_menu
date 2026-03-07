import pytest

@pytest.fixture
def seeded_db(db_connection):
    # schema.sql drops and recreates all tables, giving a clean slate with correct types.
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_products.sql")
    return db_connection



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

    def test_returns_200(self, web_client):
        response = web_client.get("/search_wines")
        assert response.status_code == 200
    
    def test_returns_all_wines_with_no_query(self, web_client, seeded_db):
        response = web_client.get("/search_wines")
        assert b'Malbec Reserva' in response.data
        assert b'Prosecco' in response.data

    def test_filters_wines_by_search_query(self, web_client, seeded_db):
          response = web_client.get("/search_wines?q=malbec")
          assert b'Malbec Reserva' in response.data
          assert b'Prosecco' not in response.data

    def test_returns_no_results_message_when_no_match(self, web_client, seeded_db):
        response = web_client.get("/search_wines?q=zzznomatch")
        assert b'No wines found' in response.data

class TestWineModalRoute:

    def test_returns_200(self, web_client):
        response = web_client.get("/wines/1/modal")
        assert response.status_code == 200
    
    def test_returns_wine(self, web_client):
        response = web_client.get("/wines/1/modal")
        assert b'Malbec Reserva' in response.data
    
    def test_returns_404_if_no_wine(self, web_client):
        response = web_client.get("/wines/10/modal")
        assert response.status_code == 404


class TestSpiritsRoute:

    def test_returns_200(self, web_client):
        response = web_client.get("/spirits")
        assert response.status_code == 200