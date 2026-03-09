from playwright.sync_api import Page, expect
import pytest



def test_home_button(page):
    page.goto("/softs")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")

def test_returns_softs_list(page, seeded_db_products):
    page.goto("/softs")
    expect(page.locator("text=Coca-Cola")).to_be_visible()
    expect(page.locator("text=Orange Juice")).to_be_visible()

def test_softs_grouped_by_subcategory(page, seeded_db_products):
    page.goto("/softs")
    expect(page.locator("h2", has_text="Classic")).to_be_visible()
    expect(page.locator("h2", has_text="Juice")).to_be_visible()

def test_soft_shows_price(page, seeded_db_products):
    page.goto("/softs")
    expect(page.locator("text=£2.50")).to_be_visible()
    expect(page.locator("text=£3.00")).to_be_visible()
