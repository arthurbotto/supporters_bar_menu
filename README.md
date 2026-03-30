# Supporters House Bar — Digital Menu

A Flask-based digital bar menu for browsing all drink categories.

> **Work in progress** — actively being developed.

---

## What it is

A web app serving as the in-house menu for Supporters House Bar. Customers can browse cocktails, mocktails, wines, spirits, beers, soft drinks and hot drinks — search by name or ingredient, expand ingredient accordions, and open modals with full item details. Built with Flask, PostgreSQL, HTMX for live search, and vanilla JS for modals.

---

## Features

- **Cocktails** — listed by subcategory ("From our menu" / "Classics"), ingredient accordion, live search (HTMX), spirit type filter with Apply/Clear, detail modal
- **Mocktails** — flat list with name and price
- **Wines** — catalogue grouped by subcategory (red, white, rosé, sparkling, dessert), price columns by serve size, live search, multi-filter bar (country, type, producer, organic, vegan, sweetness, body, acidity) with Apply/Clear, detail modal
- **Spirits** — grouped by subcategory (gin, vodka, rum, tequila, whisky, vermouth, liqueur, brandy), price columns by serve size
- **Beers** — flat list with price columns per serve size
- **Soft Drinks** — grouped by subcategory (classic, juice, fever tree, san pellegrino, water)
- **Hot Drinks** — flat list with name and price
- **Search** — ranked results: name matches scored above ingredient matches, using PostgreSQL `ILIKE` and word-boundary regex
- **is_active flag** — products can be hidden from all menus without being deleted, controlled via CSV or directly in the DB
- **Admin panel** — password-protected area at `/admin/`; full CRUD for products and cocktails; manage serve sizes and prices (variants); manage cocktail recipes (ingredients, amounts, units); wine-specific fields (region, vintage, sweetness, body, acidity); image upload for cocktails and wines; CSRF protection on all forms; login rate-limited
- **Mobile responsive** — all menu and admin pages adapt to small screens; price columns tighten, form rows stack to single column, tables scroll horizontally
- **Architecture** — repository pattern, psycopg v3 with `dict_row` results, per-request DB connection via Flask's `g` object

---

## Tech stack

- Python / Flask
- PostgreSQL + psycopg v3
- HTMX (live search, initial list load, no full page reloads)
- Vanilla JS (modals, event-delegation accordion)
- Jinja2 templates
- Playwright (E2E tests)

---

## Local setup

### Prerequisites

- Python 3.x
- PostgreSQL

### Steps

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv bar_menu_venv
   source bar_menu_venv/bin/activate  # Windows: bar_menu_venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the databases:
   ```bash
   createdb supporters_bar_menu
   createdb supporters_bar_menu_test
   ```

4. Run the schema:
   ```bash
   psql supporters_bar_menu < seeds/schema.sql
   ```

5. Start the dev server:
   ```bash
   python app.py
   ```
   App runs at [http://localhost:5001](http://localhost:5001)

---

## Populating the database

Menu data is managed via CSV files in `data/` and imported with a script:

| File | Contents |
|---|---|
| `data/products_base.csv` | All products (name, category, subcategory, producer, country, ABV, vegan, organic, is_active) |
| `data/wine_details.csv` | Wine-only fields (region, vintage), keyed by product code |
| `data/product_variants.csv` | Serve sizes and prices per product, keyed by product code |
| `data/cocktails.csv` | Cocktail definitions (including subcategory) |
| `data/ingredients.csv` | Ingredients |
| `data/recipe_items.csv` | Cocktail recipes (ingredient, amount, unit, sort order) |

To import:
```bash
python scripts/import_from_csv_v4.py
```

The script upserts — existing records are updated, not duplicated. It auto-generates product codes from category + name + producer if none are provided in the CSV, and prints generated codes at the end for reference.

Wine product codes are **year-free** (e.g. `wine_chablis_jean_marc_brocard`). Vintage lives in `wine_details.csv` only. Updating a vintage year re-imports cleanly without orphaned rows.

To hide a product from all menus without deleting it, set `is_active` to `FALSE` in the CSV and re-run the importer.

---

## Running tests

```bash
# All unit + integration tests (with coverage)
pytest tests/ --cov=app --cov-report=term-missing

# E2E tests (Playwright — requires Flask server to start)
pytest tests/e2e/

# All tests
pytest
```

251 tests total. Unit/integration tests cover all repositories, all Flask routes, and all admin CRUD routes (auth protection, product/variant management, toggle active). E2E tests cover every customer-facing page plus admin login, HTMX admin search, and JS-driven product form behaviour (category toggle, subcategory input swap, wine field visibility).

---

## Project structure

```
app.py                  # Flask routes
lib/
  cocktail.py / cocktail_repository.py
  ingredient.py / ingredient_repository.py
  recipe_item.py / recipe_item_repository.py
  product.py / product_repository.py
  product_variant.py
  database_connection.py
templates/              # Jinja2 templates + HTMX/modal fragments
static/
  css/
  js/
    admin/          # admin-specific scripts (product_form.js)
seeds/
  schema.sql
  test_cocktails.sql
  test_products.sql
data/                   # CSV source files for importer
scripts/
  import_from_csv_v4.py
tests/
  conftest.py
  test_cocktail_repository.py
  test_product_repository.py
  test_ingredient_repository.py
  test_recipe_item_repository.py
  test_app.py
  e2e/
    conftest.py
    test_home.py
    test_cocktails.py
    test_wines.py
    test_spirits.py
    test_mocktails.py
    test_beers.py
    test_softs.py
    test_hot_drinks.py
```

---

## What's coming next

- Deployment (evaluating AWS EC2 vs Render)
