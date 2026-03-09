from playwright.sync_api import Page, expect
import pytest



def test_home_button(page):
    page.goto("/spirits")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")

def test_returns_spirits_list(page, seeded_db_products):
    page.goto("/spirits")
    expect(page.locator("text=Hendricks Gin")).to_be_visible()
    expect(page.locator("text=Grey Goose")).to_be_visible()

def test_spirits_grouped_by_subcategory(page, seeded_db_products):
    page.goto("/spirits")
    expect(page.locator("h2", has_text="Gin")).to_be_visible()
    expect(page.locator("h2", has_text="Vodka")).to_be_visible()

def test_spirit_shows_name_country_abv(page, seeded_db_products):
    page.goto("/spirits")
    expect(page.locator("text=Hendricks Gin, Scotland - 41.4%")).to_be_visible()
    expect(page.locator("text=Grey Goose, France - 40.0%")).to_be_visible()

def test_spirit_shows_price(page, seeded_db_products):
    page.goto("/spirits")
    expect(page.locator("text=£9.00")).to_be_visible()
    expect(page.locator("text=£9.50")).to_be_visible()
