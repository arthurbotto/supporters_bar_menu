from playwright.sync_api import Page, expect


def test_home_button(page, seeded_db_products):
    page.goto("/snacks")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")


def test_returns_snacks_list(page, seeded_db_products):
    page.goto("/snacks")
    expect(page.locator(".product-name").filter(has_text="Crisps")).to_be_visible()
    expect(page.locator(".product-name").filter(has_text="Olives")).to_be_visible()


def test_snack_shows_price(page, seeded_db_products):
    page.goto("/snacks")
    expect(page.locator("text=£2.50")).to_be_visible()


def test_snack_shows_vegan_label(page, seeded_db_products):
    page.goto("/snacks")
    # Crisps is vegan — should show (ve)
    expect(page.locator("text=(ve)")).to_be_visible()
