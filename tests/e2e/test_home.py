from playwright.sync_api import Page, expect

#Because I created the fixture base_url in conftest.py
#the only argument needed for those tests is 'page'
#better explanation in conftest.py file.

def test_home_page_h1_tag(page):
    page.goto("/")
    h1 = page.locator("h1")
    expect(h1).to_have_text("Supporters House Bar Menu")

def test_home_cocktail_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Cocktails").click()
    expect(page).to_have_url("/cocktails")

def test_home_mocktial_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Mocktails").click()
    expect(page).to_have_url("/mocktails")

def test_home_wines_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Wines").click()
    expect(page).to_have_url("/wines")

def test_home_spirits_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Spirits").click()
    expect(page).to_have_url("/spirits")

def test_home_beer_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Beers").click()
    expect(page).to_have_url("/beers")

def test_home_softs_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Soft Drinks").click()
    expect(page).to_have_url("/softs")

def test_home_hot_drinks_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Hot Drinks").click()
    expect(page).to_have_url("/hot-drinks")

def test_home_snacks_tile_redirects_correctly(page):
    page.goto("/")
    page.get_by_role("link", name="Bar Snacks").click()
    expect(page).to_have_url("/snacks")
    


