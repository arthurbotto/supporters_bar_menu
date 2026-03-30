import re
import pytest
from playwright.sync_api import expect


# ===========================================================================
# Login
# ===========================================================================

class TestAdminLogin:

    def test_login_page_renders_form(self, page):
        page.goto("/admin/login")
        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
        expect(page.get_by_role("button", name="Log in")).to_be_visible()

    def test_invalid_credentials_shows_error(self, page):
        page.goto("/admin/login")
        page.fill("input[name='username']", "wrong")
        page.fill("input[name='password']", "wrong")
        page.get_by_role("button", name="Log in").click()
        expect(page.locator(".login-error")).to_be_visible()
        expect(page.locator(".login-error")).to_contain_text("Invalid username or password")

    def test_valid_login_grants_admin_access(self, page):
        page.goto("/admin/login")
        page.fill("input[name='username']", "testadmin")
        page.fill("input[name='password']", "testpass")
        with page.expect_navigation():
            page.get_by_role("button", name="Log in").click()
        # Session is now set — navigating to /admin should succeed (200, not redirect to login)
        page.goto("/admin")
        expect(page).to_have_url(re.compile(r"/admin$"))


# ===========================================================================
# Admin products HTMX search
# ===========================================================================

class TestAdminProductsSearch:

    def test_products_page_loads_list_via_htmx(self, logged_in_page, seeded_db_products):
        logged_in_page.goto("/admin/products")
        expect(logged_in_page.locator("text=Camden Hells")).to_be_visible()
        expect(logged_in_page.locator("text=Delisted Lager")).to_be_visible()

    def test_search_filters_products_by_name(self, logged_in_page, seeded_db_products):
        logged_in_page.goto("/admin/products")
        logged_in_page.locator("input[name='q']").press_sequentially("camden")
        expect(logged_in_page.locator("text=Camden Hells")).to_be_visible()
        expect(logged_in_page.locator("text=Guinness")).to_be_hidden()

    def test_search_includes_inactive_products(self, logged_in_page, seeded_db_products):
        logged_in_page.goto("/admin/products")
        logged_in_page.locator("input[name='q']").press_sequentially("delisted")
        expect(logged_in_page.locator("text=Delisted Lager")).to_be_visible()


# ===========================================================================
# Admin cocktails HTMX search
# ===========================================================================

class TestAdminCocktailsSearch:

    def test_cocktails_page_loads_list_via_htmx(self, logged_in_page, seeded_db_cocktails):
        logged_in_page.goto("/admin/cocktails")
        expect(logged_in_page.locator("text=Negroni")).to_be_visible()
        expect(logged_in_page.locator("text=Mojito")).to_be_visible()
        expect(logged_in_page.locator("text=Margarita")).to_be_visible()

    def test_search_filters_cocktails_by_name(self, logged_in_page, seeded_db_cocktails):
        logged_in_page.goto("/admin/cocktails")
        logged_in_page.locator("input[name='q']").press_sequentially("neg")
        expect(logged_in_page.locator("text=Negroni")).to_be_visible()
        expect(logged_in_page.locator("text=Mojito")).to_be_hidden()


# ===========================================================================
# product_form.js JS behaviour
# ===========================================================================

class TestAdminProductFormJS:

    def test_wine_fields_hidden_for_non_wine_category(self, logged_in_page, seeded_db_products):
        logged_in_page.goto("/admin/products/new")
        # Default category is blank — wine-fields should be hidden
        expect(logged_in_page.locator("#wine-fields")).to_be_hidden()

    def test_selecting_wine_shows_wine_fields(self, logged_in_page, seeded_db_products):
        logged_in_page.goto("/admin/products/new")
        logged_in_page.select_option("select#category", "wine")
        expect(logged_in_page.locator("#wine-fields")).to_be_visible()

    def test_wine_category_shows_subcategory_select(self, logged_in_page, seeded_db_products):
        logged_in_page.goto("/admin/products/new")
        logged_in_page.select_option("select#category", "wine")
        expect(logged_in_page.locator("select#subcategory-wine")).to_be_visible()
        expect(logged_in_page.locator("input#subcategory-text")).to_be_hidden()

    def test_non_wine_category_shows_subcategory_text_input(self, logged_in_page, seeded_db_products):
        logged_in_page.goto("/admin/products/new")
        logged_in_page.select_option("select#category", "beer")
        expect(logged_in_page.locator("input#subcategory-text")).to_be_visible()
        expect(logged_in_page.locator("select#subcategory-wine")).to_be_hidden()

    def test_edit_wine_prepopulates_wine_fields_visible(self, logged_in_page, seeded_db_products):
        # Product id=1 is Malbec Reserva (category=wine) — wine fields must be visible on load
        logged_in_page.goto("/admin/products/1/edit")
        expect(logged_in_page.locator("#wine-fields")).to_be_visible()
        expect(logged_in_page.locator("select#subcategory-wine")).to_be_visible()
