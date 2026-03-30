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
        env = {
            **os.environ,
            "PORT": port,
            "APP_ENV": "test",
            "ADMIN_USERNAME": "testadmin",
            "ADMIN_PASSWORD_HASH": "scrypt:32768:8:1$XWWIhSi3kxVMtbIk$06c86ab13bf5ae284eaba28a979fee28484bcf1b061df51d1ef9ef20827a69f3c2d6f402b8d958cb6edffdfc64e76210dce8a24042158d6dbdeb58ea5bf7fa05",
        }
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


@pytest.fixture
def logged_in_page(page):
    page.goto("/admin/login")
    page.fill("input[name='username']", "testadmin")
    page.fill("input[name='password']", "testpass")
    with page.expect_navigation():
        page.get_by_role("button", name="Log in").click()
    yield page