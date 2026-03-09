from playwright.sync_api import Page, expect
import pytest


def test_home_button(page):
    page.goto("/beers")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")

def test_returns_beers_list(page, seeded_db_products):
    page.goto("/beers")
    expect(page.locator("text=Camden Hells")).to_be_visible()
    expect(page.locator("text=Guinness")).to_be_visible()

def test_beer_shows_name_country_abv(page, seeded_db_products):
    page.goto("/beers")
    expect(page.locator("text=Camden Hells, England - 4.6%")).to_be_visible()
    expect(page.locator("text=Guinness, Ireland - 4.1%")).to_be_visible()

def test_beer_shows_price(page, seeded_db_products):
    page.goto("/beers")
    expect(page.locator("text=£5.50")).to_be_visible()
    expect(page.locator("text=£5.80")).to_be_visible()

def test_beer_shows_serve_size_header(page, seeded_db_products):
    page.goto("/beers")
    expect(page.locator("text=568ml")).to_be_visible()
