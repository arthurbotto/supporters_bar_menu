# Supporters Bar Menu — Project Notes

A personal log of what has been built, why decisions were made, and how things work.
Update this file whenever something meaningful changes.

---

## What This App Is

A digital bar menu for Supporters House Bar. Customers browse cocktails and wines.

- **Cocktails page** — full list, ingredient accordion, search, modal with full details
- **Wines page** — catalogue grouped by subcategory (red, white, rosé, sparkling, dessert), sorted by price; individual wine modal with full details
- **Products page** — all products (to be removed; will be replaced with per-category pages)
- **Home page** — landing page

Run with: `python app.py` (port 5001)

---

## Architecture Pattern

### Repository + Model

Every domain entity follows the same two-file pattern:

| Model (plain class, holds data) | Repository (owns all SQL) |
|---|---|
| `lib/cocktail.py` | `lib/cocktail_repository.py` |
| `lib/ingredient.py` | `lib/ingredient_repository.py` |
| `lib/recipe_item.py` | `lib/recipe_item_repository.py` |
| `lib/product.py` | `lib/product_repository.py` |
| `lib/product_variant.py` | _(no separate repo — ProductRepository handles it)_ |

**Rule:** model classes have no SQL. Repositories have no business logic.

### Why no ProductVariantRepository?

`product_variants()` lives inside `ProductRepository` because variants only ever exist
in the context of a product. A separate repository would just wrap the same queries.
The `ProductVariant` model class was still created for type consistency — so the whole
codebase returns model objects, not dicts.

### Database connection

`lib/database_connection.py` wraps psycopg v3 with `dict_row` results.
- Dev DB: `supporters_bar_menu`
- Test DB: `supporters_bar_menu_test` (activated by `APP_ENV=test`)
- Per-request singleton via Flask's `g` object (`get_flask_database_connection(app)`)

---

## Feature Log

### Cocktails (fully built)

- `GET /cocktails` — fetches all cocktails + recipe items, renders `cocktails.html`
- `GET /cocktails/<id>/modal` — AJAX fragment, returns `cocktail_modal.html`
- `GET /search` — HTMX endpoint, returns `cocktail_list.html` partial

`cocktail_list.html` is both `{% include %}`d on initial page load **and** returned
directly by `/search`. This means it works for both full render and HTMX swap without
duplicating template code.

**Search** — `CocktailRepository.search()` uses `ILIKE` for name matching and `~*`
(regex, word-boundary) for ingredient matching, with a `CASE` rank to put name matches first.

### Home page grid (updated)

`static/css/home.css` — layout expanded to match the rest of the site:

- `.grid`: `max-width` raised from `400px` → `860px` (matches `.container` width); columns changed from `1fr 1fr` → `repeat(3, 1fr)`
- `.tile`: square `aspect-ratio: 1/1` replaced with fixed `height: 180px` (landscape); added `border: 1px solid var(--border)` to match site card style; `transition` extended to include `box-shadow`
- `.tile:hover`: added `box-shadow: 0 6px 20px rgba(153, 54, 51, 0.15)` — accent-tinted lift shadow

No HTML changes were needed.

### Wines (fully built)

- `GET /wines` — renders `wines.html`
- `GET /wines/<id>/modal` — AJAX fragment, returns `wine_modal.html`
- `GET /search_wines` — HTMX endpoint, returns `wines_list.html` partial

**Route logic in `app.py` (`get_wines`):**

1. `all_wines()` — SQL query returns `Product` objects, ordered by name
2. For each wine, call `product_variants(wine.id)` → returns list of `ProductVariant` objects
3. Monkey-patch `wine.variants` and `wine.price_by_ml` onto each Product in the route
   - `wine.variants` = list of `ProductVariant` objects
   - `wine.price_by_ml` = `{serve_ml: price}` dict (convenient for template lookups)
4. Group into `grouped` dict: `{subcategory: [wine, wine, ...]}`
5. Sort each group by cheapest serve: `lambda w: min(w.price_by_ml.values())`
6. Build `section_sizes` per subcategory (for column headers in the table)
7. Enforce display order via `section_order = ['red', 'white', 'rose', 'sparkling', 'dessert']`

`wine_modal.js` listens for clicks on `.more-button-wines`, fetches the fragment from
`/wines/<id>/modal`, and injects it into `#wineModalBody`. Same pattern as the cocktail modal.

**Wine search** follows the exact same partial pattern as cocktail search:

- The initial search implementation had issues: the route was returning the full wines.html template instead of just the list partial, the repository search wasn't filtering by category or joining wine details, and the partial
didn't exist yet. I fixed this by extracting wines_list.html from the main template and refactoring the route to return only that partial.

- `wines_list.html` — partial extracted from `wines.html`; contains all the section/grouping markup
- `wines.html` now does `{% include "wines_list.html" %}` for the initial page load
- `/search_wines` runs the same grouping/sorting/section_sizes logic as `/wines`, then returns `wines_list.html` (the partial only — not the full page)
- HTMX on the search input: `hx-get="/search_wines"`, `hx-target="#wineResults"`, `hx-swap="innerHTML"`, `hx-trigger="keyup changed delay:300ms"`
- `ProductRepository.search(query)` — filters `WHERE p.category = 'wine'` and LEFT JOINs `wine_details` so region/vintage are populated in results

`ProductRepository.find_wine(parameter, column)` — fetches a single wine with a LEFT JOIN
on `wine_details`. The `column` argument lets callers look up by `id` or `code`.

**Why monkey-patch instead of putting variants on the Product model?**
Variants require a DB call per product. The model class should not know about the database.
The route is the right place to fetch and attach extra data.

### ProductVariant model (added)

`lib/product_variant.py` — fields: `id, product_id, serve_label, serve_ml, price, sort_order`

Added `__eq__` for test comparisons, `__repr__` for debugging.
`_row_to_variants()` private helper in `ProductRepository` maps DB rows to `ProductVariant` objects,
consistent with the existing `_row_to_product()` pattern.

---

## Frontend Pattern

### HTMX vs vanilla JS

| Feature | Approach | Why |
|---|---|---|
| Search | HTMX (`hx-get`, `hx-target`) | Declarative, no JS needed |
| Accordion | Event delegation on `document` | HTMX replaces the DOM on search — per-element listeners attached at page load would be lost |
| Cocktail modal | `fetch()` + HTML injection | Fetches `/cocktails/<id>/modal` fragment, injects into `#modalBody` |
| Wine modal | `fetch()` + HTML injection | Fetches `/wines/<id>/modal` fragment via `wine_modal.js`, same pattern as cocktail modal |

### CSS structure

| File | What it covers |
|---|---|
| `base.css` | Shared classes: `.product-name` (1.125rem), `.product-price-cell` (1.125rem), layout primitives |
| `cocktails.css` | `.cocktail-toggle` (flex, full-width button), accordion panel, modal, search input |
| `wines.css` | `.more-button-wines` (block, full-width button), `.wine-price-row` (grid), `.wine-price-header`, `.wine-price-cell` |

**The accordion evolution:** the original `menu.js` (kept in `old_menu_dot_js.md` for reference)
attached `addEventListener` to each `.cocktail-toggle` on page load. After HTMX was added for search,
those listeners broke because HTMX swaps out the DOM. The fix was event delegation — one listener
on `document` that checks `e.target` at click time, so it always works regardless of DOM swaps.

---

## Tests

### Current coverage

| File | Tests | Classes |
|---|---|---|
| `tests/test_cocktail_repository.py` | 22 | TestAll, TestFindCocktail, TestSearch |
| `tests/test_database_connection.py` | exists | — |
| ProductRepository | none yet | — |
| RecipeItemRepository | none yet | — |
| IngredientRepository | none yet | — |

Run all tests: `pytest`
Run one file: `pytest tests/test_cocktail_repository.py`

### Test fixtures (`tests/conftest.py`)

- `db_connection` — TestMode DB connection, seeded per test, closed after
- `test_web_address` — starts Flask test server on random port 4000–4999
- `web_client` — Flask test client with `TESTING=True`

### Test pattern to follow

See `test_cocktail_repository.py` as the reference. Tests are class-based, one class per method:
```
class TestAll:       → tests for repo.all()
class TestFind:      → tests for repo.find()
```
Each test class gets a `seeded_db` fixture that seeds schema + test data before each test.

---

## Practice / Learning Files

- `practice_wines.py` — standalone script simulating `get_wines()` without a DB.
  Useful for visualising what `grouped`, `wine.variants`, and `wine.price_by_ml` look like
  at each step. Run with `python practice_wines.py`.

---

## What Still Needs Doing (priority order)

### High value
- [ ] Tests for `ProductRepository` — follow class-based pattern (TestAll, TestAllWines, TestFind, TestFindByCode, TestProductVariants)
- [ ] Tests for `RecipeItemRepository` — test `for_cocktail()`: correct items, sort_order, empty case

### Medium
- [ ] Tests for `IngredientRepository`
- [ ] Route integration tests using `web_client` fixture (currently unused)
- [x] ~~Wine search~~ — built (`wines_list.html` partial, `/search_wines` HTMX endpoint, `ProductRepository.search()`)

### Stretch
- [ ] Remove `/products`; replace with per-category pages (`/beers`, `/spirits`, `/soft-drinks`, `/coffee`, etc.) — `category` column already in DB
- [x] ~~Individual wine detail page~~ — built (wine modal, mirrors cocktail modal pattern)
- [ ] Rate-limit `/search` with Flask-Limiter (already in `requirements.txt`)
- [ ] Playwright E2E tests (already in `requirements.txt`)

---

## Known Issues / Technical Debt

- `wine.variants` and `wine.price_by_ml` are monkey-patched onto `Product` in the route.
  The `Product` model has no default `variants = []` field, so accessing it before the route
  populates it would raise `AttributeError`. Minor — not urgent.
- Unused dependencies in `requirements.txt`: Flask-Limiter, Flask-WTF, playwright, python-slugify.
  None are wired into `app.py` yet.
- `/products` route fetches all products with no grouping — will be removed entirely and replaced with per-category pages (`/beers`, `/spirits`, `/soft-drinks`, `/coffee`, etc.).
