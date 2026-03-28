from playwright.sync_api import Page, expect
import pytest


def test_home_button(page):
    page.goto("/hot-drinks")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")

def test_returns_hot_drinks_list(page, seeded_db_products):
    page.goto("/hot-drinks")
    expect(page.locator("text=Espresso")).to_be_visible()
    expect(page.locator("text=English Breakfast Tea")).to_be_visible()

def test_hot_drink_shows_price(page, seeded_db_products):
    page.goto("/hot-drinks")
    expect(page.locator("text=£2.50").first).to_be_visible()

def test_hot_drink_shows_description(page, seeded_db_products):
    page.goto("/hot-drinks")
    expect(page.locator("text=Strong and bold")).to_be_visible()
