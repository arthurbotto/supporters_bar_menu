import pytest, sys, random, os
from pathlib import Path
from xprocess import ProcessStarter
from lib.database_connection import DatabaseConnection
from app import app


@pytest.fixture
def seeded_db_products(db_connection):
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_products.sql")
    return db_connection

@pytest.fixture
def seeded_db_cocktails(db_connection):
    db_connection.seed("seeds/schema.sql")
    db_connection.seed("seeds/test_cocktails.sql")
    return db_connection



@pytest.fixture
def db_connection():
    conn = DatabaseConnection(test_mode=True)
    conn.connect()
    yield conn
    conn.connection.close()

@pytest.fixture(scope="session")
def test_web_address(xprocess):
    python_executable = sys.executable
    app_file = Path(__file__).parent.parent.parent / "app.py"
    port = str(random.randint(8100, 8900))
    class Starter(ProcessStarter):
        env = {"PORT": port, "APP_ENV": "test", **os.environ}
        pattern = "Debugger PIN"
        args = [python_executable, app_file]

    xprocess.ensure("flask_test_server", Starter)

    yield f"localhost:{port}"

    xprocess.getinfo("flask_test_server").terminate()





# pytest-playwright provides the page fixture internally. 
# That page is created from a browser context, 
# and when creating that context it looks for a fixture named exactly base_url 
# that's a convention built into the plugin. 
# If it finds one, it uses its value as the base URL for the context.

# The chain is:
#  1. The base_url fixture depends on test_web_address
#  2. pytest-playwright's page fixture depends on base_url (by name, automatically)
#  3. The test just asks for page, everything else resolves through the dependency chain

@pytest.fixture(scope="session")
def base_url(test_web_address):
    return f"http://{test_web_address}"