from playwright.sync_api import Page, expect
import pytest


def test_home_button(page):
    page.goto("/mocktails")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")

def test_returns_mocktails_list(page, seeded_db_products):
    page.goto("/mocktails")
    expect(page.locator("text=Virgin Mojito")).to_be_visible()
    expect(page.locator("text=Shirley Temple")).to_be_visible()

def test_mocktail_shows_description(page, seeded_db_products):
    page.goto("/mocktails")
    expect(page.locator("text=Mint and lime")).to_be_visible()
    expect(page.locator("text=Ginger and cherry")).to_be_visible()

def test_mocktail_shows_price(page, seeded_db_products):
    page.goto("/mocktails")
    expect(page.locator("text=£6.00").first).to_be_visible()
