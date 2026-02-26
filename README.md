# Supporters House Bar — Digital Menu

A Flask-based digital bar menu for browsing cocktails and wines.

> **Work in progress** — actively being developed.

---

## What it is

A web app serving as the in-house menu for Supporters House Bar. Customers can browse cocktails and wines, search by name or ingredient, expand ingredient accordions, and open modals with full item details. Built with Flask, PostgreSQL, HTMX for live search, and vanilla JS for modals.

---

## Features (built so far)

- **Cocktails** — full listing, ingredient accordion, live search (HTMX), detail modal
- **Wines** — catalogue grouped by subcategory (red, white, rosé, sparkling, dessert), price columns by serve size, detail modal
- **Search** — ranked results: name matches scored above ingredient matches, using PostgreSQL `ILIKE` and word-boundary regex
- **Architecture** — repository pattern, psycopg v3 with `dict_row` results, per-request DB connection via Flask's `g` object

---

## Tech stack

- Python / Flask
- PostgreSQL + psycopg v3
- HTMX (live search, no full page reloads)
- Vanilla JS (modals, event-delegation accordion)
- Jinja2 templates

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

5. Copy `.env.example` to `.env` and fill in your `DATABASE_URL`:
   ```bash
   cp .env.example .env
   ```

6. Start the dev server:
   ```bash
   python app.py
   ```
   App runs at [http://localhost:5001](http://localhost:5001)

---

## Running tests

```bash
pytest
```

---

## Project structure

```
app.py                  # Flask routes
lib/
  cocktail_repository.py
  ingredient_repository.py
  recipe_item_repository.py
  product_repository.py
  database_connection.py
templates/              # Jinja2 templates + HTMX/modal fragments
static/
  css/
  js/
seeds/
  schema.sql
tests/
  conftest.py
  test_cocktail_repository.py
```

---

## What's coming next

- Per-category product pages (`/beers`, `/spirits`, `/soft-drinks`, etc.) — replacing the placeholder `/products` route
- Tests for `ProductRepository`, `RecipeItemRepository`, and `IngredientRepository`
- Wine search — HTMX live search, same pattern as cocktail search
- Rate limiting on `/search` — Flask-Limiter already in requirements
- Playwright E2E tests — already in requirements
