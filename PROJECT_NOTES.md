# Supporters Bar Menu — Project Notes

A personal log of what has been built, why decisions were made, and how things work.
Update this file whenever something meaningful changes.

---

## What This App Is

A digital bar menu for Supporters House Bar. Customers browse all drink categories.

- **Cocktails page** — full list grouped by subcategory ("From our menu" / "Classics"), ingredient accordion, search, modal with full details
- **Mocktails page** — flat list with name and price
- **Wines page** — catalogue grouped by subcategory (red, white, rosé, sparkling, dessert), sorted by price; individual wine modal with full details
- **Spirits page** — grouped by subcategory (gin, vodka, rum, tequila, whisky, vermouth, liqueur, brandy), sorted by cheapest serve
- **Beers page** — flat list with price columns per serve size
- **Soft Drinks page** — grouped by subcategory (fever_tree, san_pellegrino, classic, juice, water)
- **Hot Drinks page** — flat list with name and price
- **Home page** — landing page with tiles linking to all category pages

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

### Routes

| Route | Template | Notes |
|---|---|---|
| `GET /` | `home.html` | |
| `GET /cocktails` | `cocktails.html` | shell route |
| `GET /cocktails/<id>/modal` | `cocktail_modal.html` | AJAX fragment |
| `GET /search_cocktails` | `cocktail_list.html` | HTMX partial — groups by subcategory |
| `GET /wines` | `wines.html` | shell route |
| `GET /wines/<id>/modal` | `wine_modal.html` | AJAX fragment |
| `GET /search_wines` | `wines_list.html` | HTMX partial |
| `GET /spirits` | `spirits.html` | grouped by subcategory |
| `GET /mocktails` | `mocktails.html` | flat list |
| `GET /beers` | `beers.html` | flat list, price columns per serve |
| `GET /softs` | `softs.html` | grouped by subcategory |
| `GET /hot-drinks` | `hot_drinks.html` | flat list |

`GET /products` has been removed.

### Cocktails (fully built)

- `GET /cocktails` — shell route; renders `cocktails.html` with no data. Cocktail list loads via HTMX `hx-trigger="load, keyup changed delay:300ms"` calling `/search_cocktails`
- `GET /cocktails/<id>/modal` — AJAX fragment, returns `cocktail_modal.html`
- `GET /search_cocktails` — HTMX endpoint, returns `cocktail_list.html` partial; handles both initial load and live search

**Subcategory grouping** — cocktails have a `subcategory` field (`'from_menu'` or `'classic'`). `search_cocktails` in `app.py` groups by subcategory and passes `section_order = ['from_menu', 'classic']`. `cocktail_list.html` uses a `section_labels` mapping dict to display human-readable headings ("From our menu", "Classics").

**Search** — `CocktailRepository.search_cocktail()` uses `ILIKE` for name matching and `~*`
(regex, word-boundary) for ingredient matching, with a `CASE` rank to put name matches first.

**Ordering** — `CocktailRepository.all()` orders by `id ASC` to ensure a stable insertion-order display.

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

**Route logic in `app.py` (`search_wines`):**

`/wines` is a shell — renders `wines.html` with no data. The wine list loads via HTMX `hx-trigger="load, keyup changed delay:300ms"` on the search input, calling `/search_wines`. This means all grouping/sorting logic lives in one place only.

1. `all_wines()` — SQL query returns active `Product` objects, ordered by name
2. For each wine, call `product_variants(wine.id)` → returns list of `ProductVariant` objects
3. `wine.variants` and `wine.price_by_ml` set on each Product in the route
   - `wine.price_by_ml` = `{serve_ml: price}` dict (convenient for template lookups)
4. Group into `grouped` dict: `{subcategory: [wine, wine, ...]}`
5. Sort each group by cheapest serve: `lambda w: min(w.price_by_ml.values())`
6. Build `section_sizes` per subcategory (for column headers in the table)
7. Enforce display order via `section_order = ['red', 'white', 'rose', 'sparkling', 'dessert']`

`wine_modal.js` listens for clicks on `.more-button-wines`, fetches the fragment from
`/wines/<id>/modal`, and injects it into `#modalBody`. Same pattern as the cocktail modal.

### Spirits (fully built)

- `GET /spirits` — grouped by subcategory (gin, vodka, rum, tequila, whisky, vermouth, liqueur, brandy), sorted by cheapest serve within each section
- Same grouping/`section_sizes` pattern as wines
- `all_spirits()` in `ProductRepository` — filters `is_active = TRUE`

### Mocktails (fully built)

- `GET /mocktails` — flat list, name + price; simplest category page
- `all_mocktails()` in `ProductRepository` — filters `is_active = TRUE`

### Beers (fully built)

- `GET /beers` — flat list with price columns per serve size; shared `sizes` set for column headers
- `all_beers()` in `ProductRepository` — filters `is_active = TRUE`

### Soft Drinks (fully built)

- `GET /softs` — grouped by subcategory (fever_tree, san_pellegrino, classic, juice, water)
- Same grouping pattern as wines/spirits
- `all_softs()` queries `category = 'soft'` only — juices are `category='soft', subcategory='juice'`
- `all_softs()` filters `is_active = TRUE`

### Hot Drinks (fully built)

- `GET /hot-drinks` — flat list, name + price
- `all_hot_drinks()` queries `category = 'hot'`, filters `is_active = TRUE`
- `hot_drinks.css` adds only `.hot-row` (flex, space-between); all other styles from `base.css`

### is_active field (added)

`products.is_active BOOLEAN NOT NULL DEFAULT TRUE`

- All `all_*()` and `search_wine()` methods filter by `is_active = TRUE`
- `find()`, `find_wine()`, `find_by_code()` do NOT filter — intentional for direct lookups
- Managed via `products_base.csv` and the importer — set to `FALSE` in CSV to hide a product
- Future admin UI: when built, drop `is_active` from the importer's UPDATE clause so admin changes aren't overwritten by CSV re-imports
- `test_products.sql` includes one inactive product per category for filter tests

### ProductVariant model (added)

`lib/product_variant.py` — fields: `id, product_id, serve_label, serve_ml, price, sort_order`

Added `__eq__` for test comparisons, `__repr__` for debugging.
`_row_to_variants()` private helper in `ProductRepository` maps DB rows to `ProductVariant` objects,
consistent with the existing `_row_to_product()` pattern.

### ProductRepository — full method list

| Method | Description |
|---|---|
| `all_wines()` | Active wines; LEFT JOINs `wine_details` |
| `all_spirits()` | Active spirits |
| `all_mocktails()` | Active mocktails |
| `all_beers()` | Active beers |
| `all_softs()` | Active soft drinks (`category = 'soft'`; juices are `subcategory = 'juice'`) |
| `all_hot_drinks()` | Active hot drinks (`category = 'hot'`) |
| `product_variants(product_id)` | All variants for a given product |
| `find(product_id)` | Single product by id (no is_active filter) |
| `find_wine(wine_id)` | Single wine by id with LEFT JOIN on `wine_details`; filters by `category='wine'` |
| `find_by_code(code)` | Single product by code (no is_active filter) |
| `search_wine(query='', country='', subcategory='', producer='', organic=None, vegan=None, sweetness='', body='', acidity='')` | Unified wine search + filter; all args optional; builds WHERE dynamically; LEFT JOINs `wine_details` |
| `wine_countries()` | Distinct active wine countries, alphabetical — used to populate filter dropdown |
| `wine_producer()` | Distinct active wine producers, alphabetical — used to populate filter dropdown |

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
| `base.css` | Shared layout: variables, `.header`, `.container`, `.home-btn`, `.product-list`, `.product-item`, `.product-name`, `.product-price-cell`, `.product-price-header`, `.product-price-row`, `.product-cols-*` grid rules, `.search` input |
| `home.css` | Home grid: `.grid` (3-col, max-width 860px), `.tile` (180px height, hover shadow) |
| `cocktails.css` | `.cocktail-toggle` (accordion button), `.cocktail-panel`, `.chevron`, `.ingredients`, `.more-button` |
| `wines.css` | `.more-button-wines`, `.wine-filters` container, `.filter-search`, `.filter-controls`, `.filter-select`, `.filter-apply-btn`, `.filter-clear-btn`, `.filter-checkbox-label` |
| `modal.css` | `.overlay`, `.modal`, `.close`, `.modal-title`, `.modal-description`, `.modal-meta`, `body.modal-open` |
| `spirits.css` | (empty — spirits uses base.css classes only) |
| `beers.css` | (empty — beers uses base.css classes only) |
| `mocktails.css` | (empty — mocktails uses base.css classes only) |
| `softs.css` | (empty — softs uses base.css classes only) |
| `hot_drinks.css` | `.hot-row` (flex, space-between) |

**The accordion evolution:** the original `menu.js` (kept in `old_menu_dot_js.md` for reference)
attached `addEventListener` to each `.cocktail-toggle` on page load. After HTMX was added for search,
those listeners broke because HTMX swaps out the DOM. The fix was event delegation — one listener
on `document` that checks `e.target` at click time, so it always works regardless of DOM swaps.

---

## Tests

### Unit / Integration tests (`tests/`)

**Repository tests** (all complete):

| File | Classes |
|---|---|
| `tests/test_cocktail_repository.py` | TestAll, TestFindCocktail, TestSearch |
| `tests/test_product_repository.py` | TestAllWines, TestAllSpirits, TestAllBeers, TestAllSofts, TestAllHotDrinks, TestAllMocktails, TestProductVariants, TestFind, TestFindWine, TestFindByCode, TestSearchWine, TestIsActiveFilter |
| `tests/test_ingredient_repository.py` | TestAllIngredients, TestFindIngredient |
| `tests/test_recipe_item_repository.py` | TestForCocktail |

**Route tests** (all complete):

| File | Classes |
|---|---|
| `tests/test_app.py` | TestHomeRoute, TestWineRoute, TestSearchWinesRoute, TestWineModalRoute, TestSpiritsRoute, TestCocktailsRoute, TestSearchCocktailsRoute, TestCocktailModalRoute, TestMocktailsRoute, TestBeersRoute, TestSoftsRoute, TestHotDrinksRoute, TestErrorHandlers |

**Coverage:** `pytest tests/ --cov=app --cov-report=term-missing` → 98% (only error handlers and `__main__` block uncovered). Run `tests/` not `tests/e2e/` — E2E tests use a subprocess and don't contribute to coverage.

### E2E tests (`tests/e2e/`)

Playwright + pytest-playwright + xprocess. Covers all routes.

| File | What it tests |
|---|---|
| `test_home.py` | tile links |
| `test_cocktails.py` | list render, search, accordion (expand/collapse/one-at-a-time), modal (open, details, close, Escape, click-outside) |
| `test_wines.py` | list render, detail fields, (ve) label, null vintage, search, modal |
| `test_spirits.py` | list, subcategory headings, detail string, prices |
| `test_mocktails.py` | list, descriptions, prices |
| `test_beers.py` | list, detail string, prices, serve size header |
| `test_softs.py` | list, subcategory headings, prices |
| `test_hot_drinks.py` | list, prices |

- Shared fixtures in `tests/e2e/conftest.py`: `seeded_db_products`, `seeded_db_cocktails`
- Server port range: `8100–8900` (avoids Chromium unsafe ports like 4045)

### Test fixtures

- `tests/conftest.py` — `db_connection`, `web_client`
- `tests/e2e/conftest.py` — `db_connection`, `seeded_db_products`, `seeded_db_cocktails`, `base_url`

### Test pattern

- Repository tests: class-based, one class per method, local `seeded_db` fixture
- Route tests: `web_client` for all; `seeded_db_products` or `seeded_db_cocktails` when DB is queried; shell routes need no seed
- Error handler tests: 404 via `web_client.get('/nonexistent')`; 500 via calling `server_error()` directly inside `flask_app.test_request_context()`

---

## Data Import

`scripts/import_from_csv_v4.py` — upserts from `data/` CSV files into the production DB.

- Keyed on `product_code` (auto-generated from category+name+producer if missing in CSV)
- `is_active` column in `products_base.csv` — controls visibility on all menu pages
- `to_bool()` helper handles `true/false/yes/no/1/0`
- Re-running the importer is safe — existing records are updated, not duplicated
- Wine product codes are **year-free** — vintage lives only in `wine_details.vintage`; changing a vintage year in the CSV updates the existing row, not creates a new one

---

## Practice / Learning Files

- `practice_wines.py` — standalone script simulating `get_wines()` without a DB.
  Useful for visualising what `grouped`, `wine.variants`, and `wine.price_by_ml` look like
  at each step. Run with `python practice_wines.py`.

---

## What Still Needs Doing

- [ ] Rate-limit `/search_cocktails` and `/search_wines` with Flask-Limiter (already in `requirements.txt`)
- [ ] Admin cocktail CRUD (Phase 2 — deferred)

---

## Changelog

### 2026-03-25 — Admin UX polish (input controls, variant flow, CSS grid)

- **serve_label datalist** — `variants.html` serve_label inputs now use `<datalist>` with suggestions (Glass, Bottle, Carafe, Cup, Measure, Serve, Pint, Half, Can); still free-text for custom values. `serve_label` normalized to `.title()` in both `admin_variant_create` and `admin_variant_update` routes in `app.py`
- **Subcategory controls** — wine category now shows a `<select>` with 7 fixed values (red, white, rose, orange, sparkling, dessert, fortified); other categories show a text input with a per-category `<datalist>` (spirit: gin/vodka/rum/…, beer: lager/ale/stout/…, soft: fever_tree/classic/juice/…, hot/mocktail: empty but free-text). Datalist options are replaced dynamically via JS on category change — a single `<datalist id="subcategory-options">` element in the HTML, populated by `SUBCATEGORY_SUGGESTIONS` map in JS
- **JS extraction** — inline `<script>` removed from `product_form.html`; logic moved to `static/js/admin/product_form.js`; `toggleWineFields()` renamed `toggleCategoryFields()`; `{% block scripts %}{% endblock %}` added to `admin/base.html` so individual admin pages can load page-specific scripts
- **Variant redirect after creation** — `POST /admin/products/new` now redirects to `/admin/products/<id>/variants` instead of the products list, so the admin lands directly on the variants page after saving. Flash message updated accordingly. Hint text added to the new product form near the submit button
- **CSS custom property for price columns** — replaced all static `.product-cols-1` through `.product-cols-5` rules with a single rule using a CSS custom property: `.product-price-header, .product-price-row { grid-template-columns: 1fr repeat(var(--price-cols), 6rem); }`. Templates (`wines_list.html`, `spirits.html`, `softs.html`) updated from `class="product-cols-{{ sizes|length }}"` to `style="--price-cols: {{ sizes|length }}"`. Handles any number of serve sizes without CSS changes

### 2026-03-24 — Admin panel (Phase 1 — product management)

- Added password-protected admin area at `/admin/` — single user, credentials in `.env` (`ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH`, `SECRET_KEY`)
- Auth: Flask session + `@login_required` decorator; `werkzeug.security.check_password_hash` for password verification; `scripts/generate_admin_hash.py` generates the hash
- CSRF protection wired via `Flask-WTF`'s `CSRFProtect` (was already in requirements, now active)
- New write methods on `ProductRepository`: `all_products_for_admin`, `create_product`, `update_product`, `set_active`, `delete_product`, `upsert_wine_details`, `create_variant`, `update_variant`, `delete_variant`
- Extracted `slugify` + `make_product_code` from importer into `lib/product_code.py`; importer now imports from there
- New admin routes: login/logout, dashboard, products list (with activate/deactivate toggle), create product, edit product (with wine fields shown dynamically), delete product, manage variants (inline edit/add/delete)
- New templates: `templates/admin/` directory with `base.html`, `login.html`, `dashboard.html`, `products.html`, `product_form.html`, `variants.html`
- New `static/css/admin.css` — minimal admin styles, distinct from customer-facing app
- Phase 2 (cocktail CRUD) deferred to a future task

### 2026-03-24 — Remove `menu_sections` table (dead code cleanup)

- Dropped `menu_sections` table, its two indexes, the `section_id` FK column from `products`, and the `idx_products_section` index from `seeds/schema.sql`
- Removed `section_id` from `Product.__init__`, `self.section_id` assignment, and `__repr__`
- Removed `row["section_id"]` from `ProductRepository._row_to_product()`
- Removed `upsert_menu_section()` and `find_section_id()` functions from the importer; removed `section_id` from INSERT/UPDATE queries and the "Importing menu sections..." loop
- Deleted `data/menu_sections.csv`; removed `section_name` column from `data/products_base.csv`
- Fixed pre-existing bug in two `test_product_repository.py` assertions: `Product(...)` calls were missing `sweetness`, `body`, `acidity` positional args and would have raised `TypeError`
- All 166 tests pass

### 2026-03-23 — Stable wine product codes + wine taste profile filters

- Removed vintage year suffixes from all 29 wine product codes across `products_base.csv`, `wine_details.csv`, and `product_variants.csv` — codes are now stable (e.g. `wine_chablis_jean_marc_brocard` not `wine_chablis_jean_marc_brocard_2024`)
- Vintage continues to live in `wine_details.vintage`; changing a vintage no longer orphans the old DB row — the importer upserts the existing row
- Added `sweetness`, `body`, `acidity` columns to `wine_details` schema, importer, `Product` model, and all repository queries (`all_wines`, `find_wine`, `search_wine`)
- Extended filter bar with sweetness, body, and acidity dropdowns (hardcoded options: dry/off_dry/sweet, light/medium/full, low/medium/high)
- `search_wine()` now accepts `sweetness`, `body`, `acidity` args; builds `wd.sweetness = %s` etc. dynamically
- Wine modal (`wine_modal.html`) displays sweetness, body, acidity in the details section

### 2026-03-21 — Add multi-filter bar to wines page

- Added `wine_countries()` and `wine_producer()` to `ProductRepository` — query distinct values from active wines for dynamic dropdown options
- Replaced `search_wine(query)` with a unified `search_wine(query='', country='', subcategory='', producer='', organic=None, vegan=None)` — builds WHERE clause dynamically from optional args; handles both search and filter in one method
- Removed `filter_wines()` — dead code superseded by new `search_wine()`
- Updated `get_wines()` route to fetch countries/producers and pass `subcategory_labels` dict to template
- Updated `search_wines()` route to read filter args from `request.args` and forward to `search_wine()`
- Replaced `<div class="search">` + placeholder filter div in `wines.html` with single `<div id="wine-filters">` container; search input and Apply button both use `hx-include="#wine-filters"` so all filter state is included in every request; selects hold state passively with no HTMX attributes
- Added filter bar CSS to `wines.css`: `.wine-filters`, `.filter-search`, `.filter-controls`, `.filter-select`, `.filter-apply-btn`, `.filter-clear-btn`, `.filter-checkbox-label`
- Clear filter is `<a href="/wines">` — simple page reload, no JS needed

### 2026-03-11 — Add new wines and mocktail, update pricing, and improve wine list display

- Added Bottega Poeti Prosecco Brut DOC (glass 125ml £9 + bottle £39; Treviso, 2024)
- Added Laurent-Perrier Rosé Brut (bottle only £175; Champagne, NV)
- Added Cherry-lini Zero mocktail
- Deactivated Lanson Rosé Brut (is_active=FALSE)
- Added 125ml glass serve to several wines previously offered at 175ml only; adjusted prices across the list
- wines_list.html: NV wines now show "- NV" label when no vintage is set
- Enriched wine_details with regions and vintages (Wild Idol, Searcys Classic, Lanson Père & Fils)
- CocktailRepository.all() now orders by ID ASC
- Added .product-cols-4 grid rule to base.css

---

## Known Issues / Technical Debt

- Unused dependency in `requirements.txt`: Flask-Limiter. Not yet wired into `app.py`.
- Flask-WTF is now active (CSRF protection on all admin POST forms).
- `_normalize_query()` in `lib/product_repository.py` is defined but never called — dead code.