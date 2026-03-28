from playwright.sync_api import Page, expect
import pytest



def test_home_button(page):
    page.goto("/cocktails")
    page.get_by_role("link", name="Home").click()
    expect(page).to_have_url("/")

    

def test_returns_cocktails_list(page, seeded_db_cocktails):
    page.goto("/cocktails")
    expect(page.locator("text=Negroni")).to_be_visible()
    expect(page.locator("text=Margarita")).to_be_visible()
    expect(page.locator("text=£9.50")).to_be_visible()


# Search

def test_returns_cocktail_with_search_name(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.locator("input[name='q']").press_sequentially("negroni")
    expect(page.locator("text=Negroni")).to_be_visible()
    expect(page.locator("text=Margarita")).to_be_hidden()

def test_returns_cocktail_with_search_ingredient(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.locator("input[name='q']").press_sequentially("tequila")
    expect(page.locator("text=Margarita")).to_be_visible()
    expect(page.locator("text=Negroni")).to_be_hidden()



def test_search_no_match_shows_message(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.locator("input[name='q']").press_sequentially("zzznomatch")
    expect(page.locator("text=No cocktails found")).to_be_visible()

def test_clearing_search_restores_full_list(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.locator("input[name='q']").press_sequentially("negroni")
    expect(page.locator("text=Margarita")).to_be_hidden()
    page.locator("input[name='q']").dblclick()
    # page.keyboard.press("Control+a")
    page.keyboard.press("Backspace")
    expect(page.locator("text=Margarita")).to_be_visible()


# Accordion

def test_clicking_cocktail_expands_panel(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    panel = page.locator("#panel-1")
    expect(panel).to_be_visible()
    expect(page.get_by_role("button", name="Negroni")).to_have_attribute("aria-expanded", "true")

def test_clicking_expanded_cocktail_collapses_panel(page, seeded_db_cocktails):
    page.goto("/cocktails")
    btn = page.get_by_role("button", name="Negroni")
    btn.click()
    btn.click()
    expect(page.locator("#panel-1")).to_be_hidden()
    expect(btn).to_have_attribute("aria-expanded", "false")

def test_opening_one_panel_closes_others(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    page.get_by_role("button", name="Margarita").click()
    expect(page.locator("#panel-1")).to_be_hidden()
    expect(page.locator("#panel-3")).to_be_visible()


# Modal

def test_more_button_opens_modal(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    page.locator("[data-more-id='1']").click()
    expect(page.locator("#overlay")).to_be_visible()
    expect(page.locator("#modalBody")).to_contain_text("Negroni")

def test_modal_shows_cocktail_details(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    page.locator("[data-more-id='1']").click()
    expect(page.locator("#modalBody")).to_contain_text("Stirred")
    expect(page.locator("#modalBody")).to_contain_text("Rocks")
    expect(page.locator("#modalBody")).to_contain_text("Orange peel")

def test_close_button_dismisses_modal(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    page.locator("[data-more-id='1']").click()
    expect(page.locator("#overlay")).to_be_visible()
    page.get_by_role("button", name="Close").click()
    expect(page.locator("#overlay")).to_be_hidden()

def test_escape_key_dismisses_modal(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    page.locator("[data-more-id='1']").click()
    page.keyboard.press("Escape")
    expect(page.locator("#overlay")).to_be_hidden()

def test_clicking_outside_modal_dismisses_it(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    page.locator("[data-more-id='1']").click()
    page.locator("#overlay").click(position={"x": 10, "y": 10})
    expect(page.locator("#overlay")).to_be_hidden()


# Spirit filter

def test_spirit_filter_shows_matching_cocktails(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.locator("select[name='spirit_type']").select_option("gin")
    page.get_by_role("button", name="Apply Filters").click()
    expect(page.locator("text=Negroni")).to_be_visible()
    expect(page.locator("text=Mojito")).to_be_hidden()
    expect(page.locator("text=Margarita")).to_be_hidden()

def test_spirit_filter_works_with_empty_search(page, seeded_db_cocktails):
    # Regression: was calling all() when q='', ignoring spirit_type
    page.goto("/cocktails")
    page.locator("select[name='spirit_type']").select_option("rum")
    page.get_by_role("button", name="Apply Filters").click()
    expect(page.locator("text=Mojito")).to_be_visible()
    expect(page.locator("text=Negroni")).to_be_hidden()

def test_spirit_filter_combined_with_search(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.locator("input[name='q']").press_sequentially("neg")
    page.locator("select[name='spirit_type']").select_option("gin")
    page.get_by_role("button", name="Apply Filters").click()
    expect(page.locator("text=Negroni")).to_be_visible()
    expect(page.locator("text=Margarita")).to_be_hidden()

def test_clear_resets_spirit_filter(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.locator("select[name='spirit_type']").select_option("gin")
    page.get_by_role("button", name="Apply Filters").click()
    expect(page.locator("text=Mojito")).to_be_hidden()
    page.get_by_role("link", name="Clear").click()
    expect(page.locator("text=Mojito")).to_be_visible()
    expect(page.locator("text=Negroni")).to_be_visible()

def test_spirit_dropdown_only_contains_spirits(page, seeded_db_cocktails):
    page.goto("/cocktails")
    options = page.locator("select[name='spirit_type'] option").all_text_contents()
    assert "gin" in options
    assert "rum" in options
    assert "tequila" in options
    assert "aperitivo" not in options
    assert "sweet" not in options
    assert "orange_liqueur" not in options


# Accordion panel content

def test_expanded_panel_shows_ingredients(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    panel = page.locator("#panel-1")
    expect(panel).to_contain_text("Gin")
    expect(panel).to_contain_text("Campari")
    expect(panel).to_contain_text("Sweet Vermouth")

def test_expanded_panel_shows_description(page, seeded_db_cocktails):
    page.goto("/cocktails")
    page.get_by_role("button", name="Negroni").click()
    expect(page.locator("#panel-1")).to_contain_text("Bitter Italian classic")
