# Supporters Bar Menu — Project Notes

A personal log of what has been built, why decisions were made, and how things work.
Update this file whenever something meaningful changes.

---

## What This App Is

A digital bar menu for Supporters House Bar. Customers browse all drink categories.

- **Cocktails page** — full list grouped by subcategory ("From our menu" / "Classics"), ingredient accordion, search, spirit type filter, modal with full details
- **Mocktails page** — flat list with name and price
- **Wines page** — catalogue grouped by subcategory (red, white, rosé, sparkling, dessert), sorted by price; individual wine modal with full details
- **Spirits page** — grouped by subcategory (gin, vodka, rum, tequila, whisky, vermouth, liqueur, brandy), sorted by cheapest serve
- **Beers page** — flat list with price columns per serve size
- **Soft Drinks page** — grouped by subcategory (fever_tree, san_pellegrino, classic, juice, water)
- **Hot Drinks page** — flat list with name and price
- **Bar Snacks page** — flat list with name, vegan label, description, and price per serve size
- **Home page** — landing page with tiles linking to all category pages; footer with allergen info and pricing notes

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
| `GET /snacks` | `snacks.html` | flat list with vegan label and price per serve |

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

### Bar Snacks (fully built)

- `GET /snacks` — flat list, name + vegan label + description + price per serve size
- `all_snacks()` queries `category = 'snack'`, filters `is_active = TRUE`, ordered by id
- `snacks.css` adds only `.snack-row` (flex, space-between); all other styles from `base.css`

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
| `all_snacks()` | Active snacks (`category = 'snack'`), ordered by id |
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
| Dark mode toggle | `localStorage` + CSS variables | `darkmode.js` toggles `dark-mode` class on `<html>`; preference persisted in `localStorage`; anti-flash inline script in `<head>` applies class before CSS loads |

### CSS structure

| File | What it covers |
|---|---|
| `base.css` | Shared layout: variables, `.header`, `.container`, `.home-btn`, `.product-list`, `.product-item`, `.product-name`, `.product-price-cell`, `.product-price-header`, `.product-price-row`, `--price-cols` grid rule, `.search` input; `:root.dark-mode` variable overrides; `.theme-toggle` fixed button; `@media (max-width: 600px)` for all menu routes |
| `home.css` | Home grid: `.grid` (3-col, max-width 860px), `.tile` (180px height, hover shadow) |
| `cocktails.css` | `.cocktail-toggle` (accordion button), `.cocktail-panel`, `.chevron`, `.ingredients`, `.more-button` |
| `wines.css` | `.more-button-wines`, `.wine-filters` container, `.filter-search`, `.filter-controls`, `.filter-select`, `.filter-apply-btn`, `.filter-clear-btn`, `.filter-checkbox-label` |
| `modal.css` | `.overlay`, `.modal`, `.close`, `.modal-title`, `.modal-description`, `.modal-meta`, `body.modal-open` |
| `spirits.css` | (empty — spirits uses base.css classes only) |
| `beers.css` | (empty — beers uses base.css classes only) |
| `mocktails.css` | (empty — mocktails uses base.css classes only) |
| `softs.css` | (empty — softs uses base.css classes only) |
| `hot_drinks.css` | `.hot-row` (flex, space-between) |
| `snacks.css` | `.snack-row` (flex, space-between) |
| `static/js/darkmode.js` | `toggleTheme()` — toggles `dark-mode` class on `<html>`, saves to `localStorage`, updates button icon (☾/☀); wired via `addEventListener` on `.theme-toggle` |

**The accordion evolution:** the original `menu.js` (kept in `old_menu_dot_js.md` for reference (file deleted now))
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

**Coverage:** `pytest tests/ --cov=app --cov-report=term-missing` → 98% (not final result, this was mid project) (only error handlers and `__main__` block uncovered). Run `tests/` not `tests/e2e/` — E2E tests use a subprocess and don't contribute to coverage.

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

## Deployment

**Production URL:** https://supportersmenu.com

### Infrastructure

| Component | Service |
|---|---|
| Server | Hetzner CX23 VPS (Falkenstein) |
| Database | PostgreSQL 17, running as a container in the same Docker Compose stack (no longer managed AWS RDS) |
| Static IP | Hetzner-assigned IPv4 |
| Reverse proxy | nginx — forwards 80/443 → localhost:5001 |
| HTTPS | Certbot / Let's Encrypt (auto-renewal via systemd timer) |
| DNS | A record managed at Namecheap, pointing `supportersmenu.com` → Hetzner IPv4 |

Migrated off AWS EC2 + RDS in July 2026 — see Changelog.

### Docker

The app runs as two containers via `docker-compose.yml` on the Hetzner box:

- `db` — `postgres:17`, healthcheck (`pg_isready`), data persisted in a named volume (`pgdata`)
- `web` — builds from `Dockerfile`, depends on `db` being healthy, binds to `127.0.0.1:5001` only (nginx fronts it)
- `Dockerfile` — `python:3.13-slim` + `libpq-dev` (required for psycopg v3) + pip install + COPY app; `CMD` runs `gunicorn --bind 0.0.0.0:5001 --workers 3 app:app` (switched from the Flask dev server — `gunicorn` added to `requirements.txt`)
- `.dockerignore` — excludes venv, pycache, .env, tests/, data/, `docker-compose.yml`, `images/`
- Uploaded images persist via direct bind mounts on the `web` service: `./static/images/wine` → `/app/static/images/wine`, `./static/images/cocktails` → `/app/static/images/cocktails`
  - These directories are now gitignored — previously the uploaded images were committed straight into the repo; they were stripped out and untracked when the bind-mount setup replaced the old EC2 named-volume paths
  - Mounts survive `docker compose up -d --build` on every deploy; committed static assets (logo etc.) are unaffected

### nginx config (`/etc/nginx/conf.d/supportersmenu.conf`)

- `client_max_body_size 10M` in the 443 server block (default 1MB would reject image uploads)
- Certbot manages the SSL directives and HTTP→HTTPS redirect block

### CI/CD (GitHub Actions)

- `.github/workflows/ci.yml` — runs pytest on every push and pull request; PostgreSQL service container; ignores E2E tests
- `.github/workflows/deploy.yml` — pull-based deploy. On push to `main`, calls `ci.yml` first; if tests pass, SSHes into the Hetzner box and runs `git pull origin main && docker compose up -d --build && docker image prune -f` — the server pulls its own code rather than files being pushed to it (no more SCP step)
- Old EC2 SCP-based workflow archived as `.github/workflows/OLD_ec2_deploy.md` for reference
- GitHub secrets required: `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY` — app secrets (DB credentials, `SECRET_KEY`, admin login) now live in a `.env` file on the server itself, read directly by `docker-compose.yml`'s `${...}` interpolation, instead of being injected through Actions

### Manual deploy

`deploy.sh` — rsync files to EC2 then SSH to rebuild and restart the container. Gitignored (contains credentials). **Stale post-migration** — still targets the decommissioned EC2 host and RDS endpoint with a manual `docker run`; hasn't been rewritten for Hetzner. Do not use as-is; see "What Still Needs Doing".

### Running the CSV importer against production — open item, no working procedure yet

Production data on Hetzner was loaded once via `pg_restore` from the 7 July 2026 dump. The CSV importer has not been run against production since the migration, and there is currently no confirmed-working way to do so:

- The `db` service has no host port mapping — Postgres is reachable only from the `web` container on the Docker network now, unlike the old RDS setup with a security-group-gated public endpoint. The old "run the importer locally against a public DB endpoint" workflow no longer applies at all.
- `scripts/import_from_csv_v4.py` doesn't use `lib/database_connection.py` — it reads `DATABASE_URL` from the environment directly — but it does append `/supporters_bar_menu` to it itself, the same convention `lib/database_connection.py` uses per-request. Whether `docker compose exec web python scripts/import_from_csv_v4.py` actually lands on the right database has **not** been verified against the production `POSTGRES_DB` value — treat it as unconfirmed, not as a documented method.
- **Precondition before ever running it against production**: automated database backups must exist first. The importer upserts, and any admin changes made through the UI since 7 July 2026 exist only in the live database — a bad run has no safety net.

---

## Practice / Learning Files

- `practice_wines.py` — standalone script simulating `get_wines()` without a DB.
  Useful for visualising what `grouped`, `wine.variants`, and `wine.price_by_ml` look like
  at each step. Run with `python practice_wines.py`.

---

## What Still Needs Doing

- `_normalize_query()` in `product_repository.py` is dead code — safe to delete
- `deploy.sh` (manual/emergency deploy script) is stale post-Hetzner-migration — still targets the old EC2 host and RDS endpoint; needs a Hetzner rewrite or removal
- No automated backups exist on Hetzner yet. Until they do, the CSV importer must not be run against production — it upserts, and admin changes made through the UI since the 7 July 2026 migration only exist in the live database
- No confirmed working procedure for re-running the CSV importer against production post-migration (see Deployment section) — needs a decision once backups are in place

---

## Changelog

### 2026-07-26 — Migrate hosting from AWS EC2/RDS to Hetzner; untrack runtime images

- Migrated production off AWS EC2 + RDS onto a single Hetzner CX23 VPS running the new Compose stack; data moved via a one-off `pg_restore` from the 7 July 2026 dump (artifacts gitignored, not committed)
- `.gitignore` — `static/images/{wine,cocktails}/` no longer tracked (previously-committed upload images removed from the repo); they now persist purely via the `web` service's bind mounts on the host; also ignores one-time migration dump/tar artifacts (`supportersmenu-db-*.dump`, `supportersmenu-images-*.tar.gz`)
- `.github/workflows/deploy.yml` rewritten for a pull-based deploy (SSH in, `git pull` + `docker compose up -d --build` + `docker image prune -f`); old EC2 SCP-based workflow archived as `.github/workflows/OLD_ec2_deploy.md`
- GitHub secrets simplified to `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY` — app secrets now live in a `.env` file on the server, read directly by `docker-compose.yml`
- `deploy.sh` is now stale (still targets the decommissioned EC2 host/RDS) — needs rewriting for Hetzner or removal
- CSV importer has not been run against production since the migration; no confirmed working procedure yet (see Deployment section)

### 2026-07-21 — Docker Compose + gunicorn, prep for Hetzner migration

- Added `docker-compose.yml`: `db` (postgres:17, healthcheck, named volume `pgdata`) + `web` (builds from `Dockerfile`, depends on `db` healthy, binds `127.0.0.1:5001`, bind-mounts `static/images/{wine,cocktails}`)
- `Dockerfile` `CMD` switched from the Flask dev server to `gunicorn --bind 0.0.0.0:5001 --workers 3 app:app`
- `requirements.txt` — added `gunicorn`
- `.dockerignore` — now also excludes `docker-compose.yml` and `images/` from the build context

### 2026-04-04 — Null-ABV bug fix and regression tests

- **Bug fix** — `wines_list.html` line 26: `"%.1f"|format(wine.abv)` raised `TypeError` when `abv` is `NULL`; guarded with `if wine.abv` (same guard already applied to cocktail modal earlier)
- **Root cause** — the HTMX call to `/search_wines` returned 500, so HTMX didn't update `#wineResults`, leaving the static `{% include "wines_list.html" %}` placeholder with undefined `grouped` — showing "No wines found"
- **New seed rows** — `seeds/test_products.sql`: `WINE-NOABV` (id 24); `seeds/test_cocktails.sql`: `No ABV Cocktail` (id 4) — both with `abv = NULL`
- **New tests** — `tests/test_app.py`: `TestWineModalRoute.test_wine_modal_with_null_abv_returns_200`, `TestCocktailModalRoute.test_cocktail_modal_with_null_abv_returns_200`
- **Count assertions updated** — `test_cocktail_repository.py` and `test_product_repository.py` counts and name sets updated to reflect the extra seed rows

### 2026-04-02 — Admin activity log

- **New table** `admin_logs (id, action, entity_type, entity_id, entity_name, detail, created_at TIMESTAMPTZ DEFAULT NOW())`
- **New file** `lib/admin_log_repository.py` — no model class (logs are read as plain dicts); `log(action, entity_type, entity_id, entity_name, detail=None)` inserts a row; `all_logs(limit=200)` returns all rows newest-first
- **New route** `GET /admin/logs` → `templates/admin/logs.html` — table with Action, Entity Type, Entity Name, Detail, Time columns; `.logs-table` CSS class in `admin.css` with fixed column widths
- **Nav link** added to `templates/admin/base.html`
- **Logging added to all 13 admin write routes** in `app.py`: product create/update/delete/toggle, variant create/update/delete, cocktail create/update/delete/toggle, recipe add/update/remove
- Detail field: `active`/`inactive` for toggles; category for product/cocktail creates; `{serve_label} · £{price}` for variant writes; ingredient name for recipe changes
- `templates/admin/variants.html` — hidden `serve_label` field added to delete form so the route has it for the log
- `templates/admin/recipe.html` — hidden `ingredient_name` field added to delete form for the same reason

### 2026-04-01 — Dark mode

- **`base.css`** — `:root.dark-mode` variable overrides (bg, surface, panel, text, muted, border, accent, accent-soft); `.theme-toggle` fixed circular button (bottom-right)
- **`base.html`** — anti-flash inline script in `<head>` applies `dark-mode` class before CSS loads; `<button class="theme-toggle">` wired to `darkmode.js`
- **`static/js/darkmode.js`** — `toggleTheme()` toggles class + saves to `localStorage` + updates icon; `addEventListener` on `.theme-toggle`
- **`modal.css`** — replaced hardcoded `#fffaf2` and `#f3f4f6` with `var(--panel)` and `var(--surface)`
- **`wines.css`** — same replacements for wine modal detail box and image frame
- **Logo** — replaced screenshot PNG with transparent-background export from Canva (arch fill: none, stroke: maroon); no CSS filter needed

### 2026-04-01 — Deployment to AWS + production hardening

**App is live at https://supportersmenu.com**

- **Docker** — `Dockerfile` (python:3.13-slim + libpq-dev + pip install); `.dockerignore` excludes venv/tests/data
- **AWS EC2 + RDS** — EC2 t2/t3.micro (eu-west-2); RDS PostgreSQL db.t3.micro; Elastic IP assigned; RDS security group restricts port 5432 to EC2 private IP only
- **nginx** — reverse proxy on EC2; `client_max_body_size 10M` (default 1MB blocked image uploads); Certbot/Let's Encrypt HTTPS; HTTP→HTTPS redirect
- **GitHub Actions CI/CD** — `.github/workflows/ci.yml` (tests on every push); `.github/workflows/deploy.yml` (deploy to EC2 only if CI passes); deploy uses `appleboy/scp-action` + `appleboy/ssh-action`
- **Docker volumes** — uploaded images persisted at `/home/ec2-user/bar-menu-images/{wine,cocktails}` on EC2 host; survive container rebuilds on every deploy; committed static assets unaffected
- **Session timeout** — `PERMANENT_SESSION_LIFETIME = timedelta(hours=2)`; `session.permanent = True` at login; sessions expire after 2 hours

### 2026-03-31 — Comprehensive test coverage pass

**352 tests total (up from ~180), all passing. Coverage: 89% on app.py (up from ~85%).**

- `seeds/test_products.sql` — added 2 active snacks + 1 inactive + variants
- `test_product_repository.py` — `TestAllSnacks` (5 tests), extended `TestSearchProduct` with category filter tests; fixed `image_url` arg in existing write tests; fixed hot drinks ordering (now `ORDER BY p.name`)
- `test_cocktail_repository.py` — `TestCocktailAdminWrite`: create/update/set_active/delete
- `test_ingredient_repository.py` — `TestFindIngredientByName`, `TestCreateIngredient`, `TestUpdateIngredient`
- `test_recipe_item_repository.py` — `TestCreateRecipe`, `TestUpdateRecipe`, `TestDeleteRecipe`
- `test_app.py` — `TestSnacksRoute`, `TestAdminProductsCategoryFilter`, `TestAdminCreateCocktail`, `TestAdminEditCocktail`, `TestAdminDeleteCocktail`, `TestAdminToggleActiveCocktail`, `TestAdminCocktailRecipe`; validation failures and 404 cases
- `tests/e2e/test_home.py` — added snacks tile redirect test
- `tests/e2e/test_snacks.py` — new file: home button, list renders, price, vegan label

### 2026-03-31 — Bar Snacks page, home footer, admin products filter polish

**Bar Snacks**
- `GET /snacks` route, `all_snacks()` repository method, `snacks.html` template, `snacks.css`
- Flat list: name, vegan label `(ve)`, description (if set), price per serve size
- Home page tile added; admin category filter updated to include `snack`

**Home page footer**
- `.footer` + `.footer-description` added to `home.html` — allergen info, pricing notes, service charge
- `home.css`: `.footer` (separator line, centred, max-width 640px); `.footer-description` (`0.78rem`, muted, `var(--muted)`)

**Admin products filter**
- Category filter changed from `<select>` to pill `<button>` elements (All + beer/hot/mocktail/soft/spirit/wine/snack)
- `search_product(query, category)` now uses dynamic WHERE — empty category returns all products; empty query returns all names
- Active button highlighted via `.active` class toggled by `static/js/admin/products.js` (extracted from inline script; loaded via `{% block scripts %}` at bottom of body)
- Admin products table: `table-layout: fixed` with explicit column widths; code column truncated with ellipsis; actions column always visible

**`templates/base.html` created**
- All customer-facing templates extend `base.html`; consistent `<head>`, admin bar link, `{% block scripts %}` slot

### 2026-03-30 — Admin cocktail CRUD, image upload, rate limiting, UX polish

**Admin cocktail CRUD**
- Full create/edit/delete and toggle-active for cocktails via admin panel
- `GET/POST /admin/cocktails/new`, `GET/POST /admin/cocktails/<id>/edit`, `POST /admin/cocktails/<id>/delete`, `POST /admin/cocktails/<id>/toggle`
- Recipe management: `GET /admin/cocktails/<id>/recipe`, `POST .../recipe/new`, `POST /admin/recipe/<id>/edit`, `POST /admin/recipe/<id>/delete`
- `admin_cocktail_new` redirects to recipe page after creation so ingredients are added immediately
- `UniqueViolation` caught on create/edit — flash error instead of 500

**Image upload with Pillow normalisation**
- `image_url VARCHAR(500)` column added to both `cocktails` and `products` tables (schema.sql updated)
- `_save_image(file, subfolder)` helper in `app.py`: validates extension, generates UUID-prefixed filename, always saves as optimised JPEG (quality 88), max 1200px
- Pillow portrait normalisation: wine images with height > 1.8× width padded to 1.5:1 ratio (bg `#f8f8f8`); cocktail images with height > 1.3× width padded to square (bg `#f3f4f6`)
- Files stored in `static/images/cocktails/` and `static/images/wine/`; `os.makedirs(..., exist_ok=True)` creates folders on first upload
- Admin forms for both cocktails and products include file input + existing image preview
- Customer modals display image in a styled frame above description; placeholder shown when no image set
- Importer unchanged — INSERT/UPDATE don't touch `image_url`, so admin-uploaded images survive re-imports
- `Pillow` added to `requirements.txt`

**Flask-Limiter (now active)**
- Admin login rate-limited: `@limiter.limit("10 per minute")` — brute force protection
- `RATELIMIT_ENABLED = False` when `APP_ENV=test` — tests unaffected
- No limits on search/menu routes (bar patrons share pub WiFi; IP-based limits would hit all customers)

**Admin form UX polish**
- Cocktail form: `method`, `glass`, `garnish` changed from `<textarea>` to `<input type="text">` with `<datalist>` suggestions; price `step` → `0.01`; ABV + price combined in one row
- Recipe form: ingredient name full-width; category + subcategory in 2-col row; amount + unit in row; order + optional in row; unit and ingredient-category `<datalist>` added; optional field changed from checkbox to `<select>` (No/Yes); confirm dialogs use `{{ name | e }}` (HTML escape, not `tojson`)
- Admin action buttons (`form-actions`) now `flex-wrap: wrap` on mobile — no longer squish

**CSS fixes**
- Overlay (`modal.css`): added `z-index: 200` — admin fixed bar no longer overlaps modal close button
- Cocktail filter (`cocktails.css`): spirit `<select>` capped at `max-width: 180px` so it doesn't dominate the bar
- Wine filter (`wines.css`): desktop `.wine-filters .filter-select` capped at `max-width: 140px`; mobile override adds `max-width: calc(50% - 4px)` so all selects fill 50% equally

### 2026-03-28 — Admin integration tests + E2E tests

- **Admin route integration tests** (`tests/test_app.py`) — 35 new tests covering all admin routes: auth protection (unauthenticated redirects), dashboard, products/cocktails HTMX search (includes inactive), toggle active, create/edit/delete product, variant CRUD. Uses new `admin_client` fixture in `tests/conftest.py` (session injection + CSRF disabled).
- **Admin E2E tests** (`tests/e2e/test_admin.py`) — 13 new Playwright tests covering: login form, invalid credentials error, valid login grants access, HTMX-driven products/cocktails search (including inactive products), `product_form.js` category toggle (wine fields show/hide), subcategory input swap (select vs text+datalist), edit form pre-populates wine fields. Test credentials injected into xprocess env; `logged_in_page` fixture added to `tests/e2e/conftest.py`.
- **Total tests: 251** (90 E2E, 161 unit/integration — up from 213 before this session).

### 2026-03-26 — Mobile responsive polish (all routes + admin)

- **Wine rows** (`wines.css`) — price columns `3.5rem`→`3rem`; price cell font `0.82rem`→`0.78rem`; `.more-button-wines` side padding `14px`→`8px`; wine name font `1.125rem`→`0.9rem` on mobile. Long names (30+ chars) now fit in ~2 lines with 3 price cols on a 375px phone
- **All menu routes** (`base.css`) — added `@media (max-width: 600px)`: title 30px→24px; header padding reduced; price columns `6rem`→`4rem`; price cell font `0.9rem`; product name `1rem`; row padding tightened. Wines page unaffected — `wines.css` overrides with higher-specificity selectors (`.more-button-wines .product-price-row`) to keep `3rem` columns
- **Cocktails** (`cocktails.css`) — added `@media (max-width: 600px)`: toggle padding `16px 14px`→`12px 10px`; font 18px→16px
- **Admin** (`admin.css`) — added `@media (max-width: 600px)`: container/nav padding reduced; `.admin-toolbar` stacks vertically (title above button); `.admin-table` → `display:block; overflow-x:auto` (handles 6-col products table and inline-width variant inputs without overflow); `.form-row` → `grid-template-columns: 1fr` (form inputs full-width, one per row); form padding reduced; search bar expands to full width

### 2026-03-25 — Admin UX polish (input controls, variant flow, CSS grid)

- **serve_label datalist** — `variants.html` serve_label inputs now use `<datalist>` with suggestions (Glass, Bottle, Carafe, Cup, Measure, Serve, Pint, Half, Can); still free-text for custom values. `serve_label` normalized to `.title()` in both `admin_variant_create` and `admin_variant_update` routes in `app.py`
- **Subcategory controls** — wine category now shows a `<select>` with 7 fixed values (red, white, rose, orange, sparkling, dessert, fortified); other categories show a text input with a per-category `<datalist>` (spirit: gin/vodka/rum/…, beer: lager/ale/stout/…, soft: fever_tree/classic/juice/…, hot/mocktail: empty but free-text). Datalist options are replaced dynamically via JS on category change — a single `<datalist id="subcategory-options">` element in the HTML, populated by `SUBCATEGORY_SUGGESTIONS` map in JS
- **JS extraction** — inline `<script>` removed from `product_form.html`; logic moved to `static/js/admin/product_form.js`; `toggleWineFields()` renamed `toggleCategoryFields()`; `{% block scripts %}{% endblock %}` added to `admin/base.html` so individual admin pages can load page-specific scripts
- **Variant redirect after creation** — `POST /admin/products/new` now redirects to `/admin/products/<id>/variants` instead of the products list, so the admin lands directly on the variants page after saving. Flash message updated accordingly. Hint text added to the new product form near the submit button
- **CSS custom property for price columns** — replaced all static `.product-cols-1` through `.product-cols-5` rules with a single rule using a CSS custom property: `.product-price-header, .product-price-row { grid-template-columns: 1fr repeat(var(--price-cols), 6rem); }`. Templates (`wines_list.html`, `spirits.html`, `softs.html`) updated from `class="product-cols-{{ sizes|length }}"` to `style="--price-cols: {{ sizes|length }}"`. Handles any number of serve sizes without CSS changes
- **Admin products search** — `GET /admin/products` converted to HTMX shell (no DB call); new `GET /admin/search_products` returns `admin/products_list.html` partial; search input uses `hx-trigger="load, keyup changed delay:300ms"` so initial load and live search share the same endpoint — same pattern as cocktails/wines; `ProductRepository.search_product(query='')` added for name/category/subcategory `ILIKE` search across all products (active + inactive); `.admin-search` CSS class added to `admin.css` (styled input with embedded SVG magnifying glass icon, focus ring)

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

### 2026-03-28 — Cocktail spirit filter, is_active on cocktails, admin cocktail list, test coverage

**Cocktail spirit filter**
- Added `subcategory` column to `ingredients` table (`seeds/schema.sql`, `lib/ingredient.py`)
- Added `spirit_types()` method to `IngredientRepository` — returns distinct subcategories where `category='spirit'`, alphabetically ordered
- Updated `search_cocktail()` in `CocktailRepository` to accept `spirit_type=''` param; builds dynamic WHERE clause (same pattern as `search_wine()`); uses PostgreSQL `\m...\M` word-boundary regex so searching "rum" matches "White Rum" but not partial strings; ranked CASE expression orders name matches above ingredient matches
- Added `<div id="cocktail-filters">` container to `cocktails.html` with spirit type `<select>` populated from backend, Apply button (`hx-include="#cocktail-filters"`), Clear link — same HTMX pattern as wine filters
- Added `.cocktail-filters` and related CSS classes to `cocktails.css`
- Updated `get_cocktails_page()` route to fetch and pass `spirits` list to template
- Fixed bug: `search_cocktails()` route was calling `cocktail_repo.all()` when `q=''`, ignoring `spirit_type`; now always calls `search_cocktail(query=q, spirit_type=spirit_type)`

**cocktails.is_active and admin cocktail list**
- Added `is_active BOOLEAN NOT NULL DEFAULT TRUE` to cocktails table
- Updated `Cocktail` model (`lib/cocktail.py`) to include `is_active` field
- `CocktailRepository.all()` and `search_cocktail()` filter by `is_active = TRUE`; new `all_cocktails_for_admin()` and `search_cocktail_admin()` methods skip that filter
- Added admin read-only routes: `GET /admin/cocktails` (shell) and `GET /admin/search_cocktails` (HTMX partial, accepts `q`)
- Updated `data/cocktails.csv` and importer (`scripts/import_from_csv_v4.py`) to handle `is_active` column

**Test coverage — 213 tests total (77 E2E, 136 unit/integration)**

E2E tests added (17 new):
- `tests/e2e/test_cocktails.py`: spirit filter (Apply with gin/rum, empty search regression, combined with text, Clear resets, dropdown contents), accordion panel content (ingredients, description)
- `tests/e2e/test_wines.py`: wine filters (country, subcategory, vegan, sweetness, body, combined, Clear resets all), modal fields (Organic: No, Sweetness/Body/Acidity), inactive wine excluded
- `tests/e2e/test_hot_drinks.py`: description field renders

Unit/integration tests added (28 new):
- `test_ingredient_repository.py`: `TestSpiritTypes` — returns only spirit subcategories, alphabetical, excludes non-spirits, empty DB
- `test_cocktail_repository.py`: `TestSearchWithSpiritFilter` — gin/rum/tequila filter, empty query regression, combined with text, no match, returns instances
- `test_product_repository.py`: `TestSearchWine` extended with country/subcategory/vegan/sweetness/body/acidity/combined/no-match/inactive filters; `TestWineCountries`; `TestWineProducer`
- `test_app.py`: wine route — country/subcategory/vegan filter params; cocktail route — spirit_type filter, spirit_type with empty q regression

Seed data updates:
- `seeds/test_products.sql`: wine_details INSERT now includes sweetness/body/acidity for all test wines (enables filter tests); Espresso description set to `'Strong and bold'`
- Fixed existing `test_product_repository.py::TestAllWines::test_returns_correct_fields` to expect `'dry'/'full'/'medium'` for Malbec after seed update

---

## Known Issues / Technical Debt

---
