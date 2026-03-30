import pytest, sys, random, os
from pathlib import Path
from xprocess import ProcessStarter
from lib.database_connection import DatabaseConnection
from app import app

@pytest.fixture
def seeded_db_products(db_connection):
    # schema.sql drops and recreates all tables, giving a clean slate with correct types.
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_products.sql")
    return db_connection

@pytest.fixture
def seeded_db_cocktails(db_connection):
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_cocktails.sql")
    return db_connection

# This is a Pytest fixture.
# It creates an object that we can use in our tests.
# We will use it to create a database connection.
@pytest.fixture
def db_connection():
    conn = DatabaseConnection(test_mode=True)
    conn.connect()
    yield conn
    conn.connection.close()

# This fixture starts the test server and makes it available to the tests.
# You don't need to understand it in detail.
@pytest.fixture
def test_web_address(xprocess):
    python_executable = sys.executable
    app_file = Path(__file__).parent / "../app.py"
    port = str(random.randint(4000, 4999))
    class Starter(ProcessStarter):
        env = {"PORT": port, "APP_ENV": "test", **os.environ}
        pattern = "Debugger PIN"
        args = [python_executable, app_file]

    xprocess.ensure("flask_test_server", Starter)

    yield f"localhost:{port}"

    xprocess.getinfo("flask_test_server").terminate()


# Now, when we create a test, if we allow it to accept a parameter called
# `db_connection` or `test_web_address`, Pytest will automatically pass in the
# objects we created above.

# For example:

# def test_something(db_connection, test_web_address):
#     # db_connection is now available to us in this test.
#     # test_web_address is also available to us in this test.


# We'll also create a fixture for the client we'll use to make test requests.
@pytest.fixture
def web_client():
    app.config['TESTING'] = True # This gets us better errors
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_client(web_client):
    app.config['WTF_CSRF_ENABLED'] = False
    with web_client.session_transaction() as sess:
        sess['admin_logged_in'] = True
    yield web_client
    app.config['WTF_CSRF_ENABLED'] = True