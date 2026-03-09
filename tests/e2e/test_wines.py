from playwright.sync_api import Page, expect
import pytest


# Basic

def test_home_button(page):
    page.goto("/wines")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")

def test_returns_wines_list(page, seeded_db_products):
    page.goto("/wines")
    expect(page.locator("text=Malbec Reserva")).to_be_visible()
    expect(page.locator("text=Rioja Crianza")).to_be_visible()
    expect(page.locator("text=Prosecco")).to_be_visible()

def test_wine_shows_prices(page, seeded_db_products):
    page.goto("/wines")
    expect(page.locator("text=£6.50").first).to_be_visible()
    expect(page.locator("text=£8.50").first).to_be_visible()


# List detail rendering

def test_wine_shows_all_detail_fields(page, seeded_db_products):
    # Malbec: country, region, vintage, abv, vegan all present
    page.goto("/wines")
    malbec = page.locator(".product-name").filter(has_text="Malbec Reserva")
    expect(malbec).to_contain_text("Argentina")
    expect(malbec).to_contain_text("Mendoza")
    expect(malbec).to_contain_text("2021")
    expect(malbec).to_contain_text("13.5%")
    expect(malbec).to_contain_text("(ve)")

def test_vegan_wine_shows_ve_label(page, seeded_db_products):
    page.goto("/wines")
    expect(page.locator(".product-name").filter(has_text="Malbec Reserva")).to_contain_text("(ve)")

def test_non_vegan_wine_hides_ve_label(page, seeded_db_products):
    page.goto("/wines")
    expect(page.locator(".product-name").filter(has_text="Rioja Crianza")).not_to_contain_text("(ve)")

def test_null_vintage_not_rendered(page, seeded_db_products):
    # Prosecco has vintage=NULL — should not render a year or "None"
    page.goto("/wines")
    prosecco = page.locator(".product-name").filter(has_text="Prosecco")
    expect(prosecco).to_contain_text("Veneto")
    expect(prosecco).to_contain_text("11.0%")
    expect(prosecco).not_to_contain_text("None")


# Search

def test_search_filters_wines(page, seeded_db_products):
    page.goto("/wines")
    page.locator("input[name='q']").press_sequentially("malbec")
    expect(page.locator("text=Malbec Reserva")).to_be_visible()
    expect(page.locator("text=Rioja Crianza")).to_be_hidden()

def test_search_no_match_shows_message(page, seeded_db_products):
    page.goto("/wines")
    page.locator("input[name='q']").press_sequentially("zzznomatch")
    expect(page.locator("text=No wines found")).to_be_visible()

def test_clearing_search_restores_full_list(page, seeded_db_products):
    page.goto("/wines")
    page.locator("input[name='q']").press_sequentially("malbec")
    expect(page.locator("text=Rioja Crianza")).to_be_hidden()
    page.locator("input[name='q']").dblclick()
    page.keyboard.press("Backspace")
    expect(page.locator("text=Rioja Crianza")).to_be_visible()


# Modal

def test_clicking_wine_opens_modal(page, seeded_db_products):
    page.goto("/wines")
    page.locator("[data-more-id='1']").click()
    expect(page.locator("#overlay")).to_be_visible()

def test_modal_shows_wine_details(page, seeded_db_products):
    # Malbec Reserva: id=1, vegan=True
    page.goto("/wines")
    page.locator("[data-more-id='1']").click()
    expect(page.locator("#modalBody")).to_contain_text("Malbec Reserva")
    expect(page.locator("#modalBody")).to_contain_text("Catena")       # producer
    expect(page.locator("#modalBody")).to_contain_text("Argentina")    # country
    expect(page.locator("#modalBody")).to_contain_text("Mendoza")      # region
    expect(page.locator("#modalBody")).to_contain_text("2021")         # vintage
    expect(page.locator("#modalBody")).to_contain_text("13.5%")        # abv
    expect(page.locator("#modalBody")).to_contain_text("Vegan: Yes")

def test_modal_shows_non_vegan(page, seeded_db_products):
    # Rioja Crianza: id=2, vegan=NULL
    page.goto("/wines")
    page.locator("[data-more-id='2']").click()
    expect(page.locator("#modalBody")).to_contain_text("Vegan: No")

def test_close_button_dismisses_modal(page, seeded_db_products):
    page.goto("/wines")
    page.locator("[data-more-id='1']").click()
    expect(page.locator("#overlay")).to_be_visible()
    page.get_by_role("button", name="Close").click()
    expect(page.locator("#overlay")).to_be_hidden()

def test_escape_key_dismisses_modal(page, seeded_db_products):
    page.goto("/wines")
    page.locator("[data-more-id='1']").click()
    page.keyboard.press("Escape")
    expect(page.locator("#overlay")).to_be_hidden()

def test_clicking_outside_modal_dismisses_it(page, seeded_db_products):
    page.goto("/wines")
    page.locator("[data-more-id='1']").click()
    page.locator("#overlay").click(position={"x": 10, "y": 10})
    expect(page.locator("#overlay")).to_be_hidden()
