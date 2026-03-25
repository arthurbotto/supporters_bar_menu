import os
from decimal import Decimal, InvalidOperation
from functools import wraps
from flask import Flask, redirect, request, render_template, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from lib.database_connection import get_flask_database_connection
from lib.cocktail_repository import CocktailRepository
from lib.product import Product
from lib.product_repository import ProductRepository
from lib.product_code import make_product_code
from lib.recipe_item_repository import RecipeItemRepository

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-fallback-change-me')
app.config['WTF_CSRF_ENABLED'] = True
csrf = CSRFProtect(app)


def _parse_decimal(value):
    s = (value or '').strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _parse_int(value):
    s = (value or '').strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated



# ----------------------
# home page
# ----------------------
@app.route('/')
def get_home_page():
    return render_template('home.html')


# ----------------------
# spirits page
# ----------------------
@app.route('/spirits')
def get_spirits():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    spirits = product_repo.all_spirits()

    grouped = {}
    section_sizes = {}

    for spirit in spirits:
        spirit.variants = product_repo.product_variants(spirit.id)
        spirit.price_by_ml = {v.serve_ml: v.price for v in spirit.variants}
        if spirit.subcategory not in grouped:
            grouped[spirit.subcategory] = []
            section_sizes[spirit.subcategory] = set()
        grouped[spirit.subcategory].append(spirit)
        for ml in spirit.price_by_ml:
            section_sizes[spirit.subcategory].add(ml)

    section_sizes = {k: sorted(v) for k, v in section_sizes.items()}

    for spirit_list in grouped.values():
        spirit_list.sort(key=lambda s: min(s.price_by_ml.values()) if s.price_by_ml else float('inf'))
    
    section_order = ['gin', 'vodka', 'rum', 'tequila', 'whisky', 'vermouth', 'liqueur', 'brandy']

    return render_template('spirits.html', grouped=grouped, section_order=section_order, section_sizes=section_sizes)

# ----------------------
# wines page
# ----------------------

# on this route, i will leave the wine logic commented, as reference.
# I realised i dont really need it here, if i change hx-trigger="load"
# on wines.html.
# to make it work with the logic again just change
# hx-trigger="keyup changed delay:300ms".
@app.route('/wines')
def get_wines():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    countries = product_repo.wine_countries()
    producers = product_repo.wine_producer()
    sweet_levels = ['dry', 'off-dry', 'sweet']
    bodies = ['light', 'medium', 'full']
    acid_levels = ['low', 'medium', 'high']
    subcategory_labels = {
        'red': 'Red', 'white': 'White', 'rose': 'Rosé', 'orange': 'Orange', 
        'sparkling': 'Sparkling', 'dessert': 'Dessert', 'fortified': 'Fortified'
        }
    return render_template('wines.html', 
                           countries=countries, 
                           subcategory_labels=subcategory_labels, 
                           producers=producers,
                           sweet_levels=sweet_levels,
                           bodies=bodies,
                           acid_levels=acid_levels) 
    # wines = product_repo.all_wines()

    # grouped = {}
    # section_sizes = {}

    # for wine in wines:
    #     wine.variants = product_repo.product_variants(wine.id)
    #     wine.price_by_ml = {v.serve_ml: v.price for v in wine.variants}
    #     if wine.subcategory not in grouped:
    #         grouped[wine.subcategory] = []
    #         section_sizes[wine.subcategory] = set()
    #     grouped[wine.subcategory].append(wine)
    #     for ml in wine.price_by_ml:
    #         section_sizes[wine.subcategory].add(ml)

    # section_sizes = {k: sorted(v) for k, v in section_sizes.items()}

    # for wines_list in grouped.values():
    #     wines_list.sort(key=lambda w: min(w.price_by_ml.values()))

    # # The order that sections should appear in the page
    # section_order = ['red', 'white', 'rose', 'sparkling', 'dessert']

    # return render_template('wines.html', grouped=grouped, section_order=section_order, section_sizes=section_sizes)

@app.route('/wines/<int:wine_id>/modal')
def wine_modal(wine_id):
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    
    wine = product_repo.find_wine(wine_id)

    if wine is None:
        return render_template('404.html'), 404

    return render_template("wine_modal.html", wine=wine)

@app.route('/search_wines')
def search_wines():
    q = request.args.get('q', '').strip()
    country = request.args.get('country', '').strip()
    subcategory = request.args.get('subcategory', '').strip()
    producer = request.args.get('producer', '').strip()
    sweetness = request.args.get('sweetness', '').strip()
    body = request.args.get('body', '').strip()
    acidity = request.args.get('acidity', '').strip()
    organic = True if request.args.get('organic') == 'true' else None
    vegan = True if request.args.get('vegan') == 'true' else None
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)

    wines = product_repo.search_wine(
        query=q, 
        country=country, 
        subcategory=subcategory, 
        producer=producer,
        sweetness=sweetness,
        body=body,
        acidity=acidity, 
        organic=organic, 
        vegan=vegan)

    
    grouped = {}
    section_sizes = {}

    for wine in wines:
        wine.variants = product_repo.product_variants(wine.id) or []
        wine.price_by_ml = {
            v.serve_ml: v.price
            for v in wine.variants 
            if v.serve_ml is not None and v.price is not None
        }
        if wine.subcategory not in grouped:
            grouped[wine.subcategory] = []
            section_sizes[wine.subcategory] = set()
        grouped[wine.subcategory].append(wine)
        for ml in wine.price_by_ml:
            section_sizes[wine.subcategory].add(ml)

    section_sizes = {k: sorted(v) for k, v in section_sizes.items()}

    for wines_list in grouped.values():
        wines_list.sort(key=lambda w: min(w.price_by_ml.values()) if w.price_by_ml else float('inf'))

    section_order = ['red', 'white', 'rose', 'orange', 'sparkling', 'dessert', 'fortified']

    return render_template('wines_list.html', grouped=grouped, section_order=section_order, section_sizes=section_sizes)


# ---------------------
# cocktails page
# ---------------------

@app.route('/cocktails')
def get_cocktails_page():
    # connection = get_flask_database_connection(app)
    # cocktail_repo = CocktailRepository(connection)
    # recipe_repo = RecipeItemRepository(connection)
    # cocktails = cocktail_repo.all()
    

    # for cocktail in cocktails:
    #     cocktail.recipe_items = recipe_repo.for_cocktail(cocktail.id)

    return render_template('cocktails.html')




@app.route('/cocktails/<int:cocktail_id>/modal')
def cocktail_modal(cocktail_id):
    connection = get_flask_database_connection(app)
    cocktail_repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)

    cocktail = cocktail_repo.find_cocktail(cocktail_id, "id")
    if cocktail is None:
        return render_template('404.html'), 404

    cocktail.recipe_items = recipe_repo.for_cocktail(cocktail.id)

    return render_template("cocktail_modal.html", cocktail=cocktail)

@app.route('/search_cocktails')
def search_cocktails():
    q = request.args.get('q', '').strip()

    connection = get_flask_database_connection(app)
    cocktail_repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)

    if q == '':
        cocktails = cocktail_repo.all()
    else:
        cocktails = cocktail_repo.search_cocktail(q)
    
    grouped = {}
    
    for cocktail in cocktails:
        cocktail.recipe_items = recipe_repo.for_cocktail(cocktail.id)
        if cocktail.subcategory not in grouped:
            grouped[cocktail.subcategory] = []
        grouped[cocktail.subcategory].append(cocktail)
    
    section_order = ['from_menu', 'classic']
    

    
    return render_template("cocktail_list.html", grouped=grouped, section_order=section_order)

# ---------------
# mocktails page
# ---------------

@app.route('/mocktails')
def get_mocktails_page():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    mocktails = product_repo.all_mocktails()

    for m in mocktails:
        m.variants = product_repo.product_variants(m.id)
    
    return render_template('mocktails.html', mocktails=mocktails)


# ---------------
# beers page
# ---------------

@app.route('/beers')
def get_beers_page():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    beers = product_repo.all_beers()

    sizes = set()

    for b in beers:
        b.variants = product_repo.product_variants(b.id)
        b.price_by_ml = {v.serve_ml: v.price for v in b.variants}
        
        for ml in b.price_by_ml:
            sizes.add(ml)
    
    return render_template('beers.html', beers=beers, sizes=sorted(sizes))


# -------------------------------
# soft drinks, juices, water page
# -------------------------------

@app.route('/softs')
def get_softs_page():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    softs = product_repo.all_softs()

    grouped = {}
    section_sizes = {}

    for s in softs:
        s.variants = product_repo.product_variants(s.id)
        s.price_by_ml = {v.serve_ml: v.price for v in s.variants}
        if s.subcategory not in grouped:
            grouped[s.subcategory] = []
            section_sizes[s.subcategory] = set()
        grouped[s.subcategory].append(s)
        for ml in s.price_by_ml:
            section_sizes[s.subcategory].add(ml)

    section_sizes = {k: sorted(v) for k, v in section_sizes.items()}
    section_order = ['fever_tree', 'san_pellegrino', 'classic', 'juice', 'water']

    return render_template('softs.html', grouped=grouped, section_order=section_order, section_sizes=section_sizes)




# ---------------
# hot drinks page
# ---------------

@app.route('/hot-drinks')
def get_hot_drinks_page():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    hot_drinks = product_repo.all_hot_drinks()

    for h in hot_drinks:
        h.variants = product_repo.product_variants(h.id)
    
    
    return render_template('hot_drinks.html', hot_drinks=hot_drinks)


# ===========================
# Admin routes
# ===========================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        expected_user = os.getenv('ADMIN_USERNAME', '')
        expected_hash = os.getenv('ADMIN_PASSWORD_HASH', '')
        if username == expected_user and expected_hash and check_password_hash(expected_hash, password):
            session['admin_logged_in'] = True
            return redirect(url_for('get_home_page'))
        error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)


@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/products')
@login_required
def admin_products():
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)
    products = repo.all_products_for_admin()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/<int:product_id>/toggle', methods=['POST'])
@login_required
def admin_toggle_active(product_id):
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)
    product = repo.find(product_id)
    if product is None:
        flash('Product not found.', 'error')
    else:
        repo.set_active(product_id, not product.is_active)
        status = 'active' if not product.is_active else 'inactive'
        flash(f'"{product.name}" set to {status}.', 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/new', methods=['GET', 'POST'])
@login_required
def admin_product_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        if not name or not category:
            flash('Name and category are required.', 'error')
            return render_template('admin/product_form.html', product=None, form=request.form)

        code = request.form.get('code', '').strip() or make_product_code(
            category, name, request.form.get('producer', '').strip() or None
        )
        subcategory = request.form.get('subcategory', '').strip().lower() or None
        description = request.form.get('description', '').strip() or None
        producer = request.form.get('producer', '').strip() or None
        country = request.form.get('country', '').strip() or None
        abv = _parse_decimal(request.form.get('abv'))
        vegan = True if request.form.get('vegan') else None
        organic = True if request.form.get('organic') else None

        connection = get_flask_database_connection(app)
        repo = ProductRepository(connection)
        product_id = repo.create_product(
            code, name, category, subcategory, description, producer, country, abv, vegan, organic
        )

        if category == 'wine':
            repo.upsert_wine_details(
                product_id,
                request.form.get('region', '').strip() or None,
                _parse_int(request.form.get('vintage')),
                request.form.get('sweetness', '').strip() or None,
                request.form.get('body', '').strip() or None,
                request.form.get('acidity', '').strip() or None,
            )

        flash(f'"{name}" created. Now add at least one serve size and price.', 'success')
        return redirect(url_for('admin_product_variants', product_id=product_id))

    return render_template('admin/product_form.html', product=None, form={})


@app.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_product_edit(product_id):
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        if not name or not category:
            flash('Name and category are required.', 'error')
            product = repo.find_wine(product_id) if category == 'wine' else repo.find(product_id)
            return render_template('admin/product_form.html', product=product, form=request.form)

        subcategory = request.form.get('subcategory', '').strip().lower() or None
        description = request.form.get('description', '').strip() or None
        producer = request.form.get('producer', '').strip() or None
        country = request.form.get('country', '').strip() or None
        abv = _parse_decimal(request.form.get('abv'))
        vegan = True if request.form.get('vegan') else None
        organic = True if request.form.get('organic') else None

        repo.update_product(
            product_id, name, category, subcategory, description, producer, country, abv, vegan, organic
        )

        if category == 'wine':
            repo.upsert_wine_details(
                product_id,
                request.form.get('region', '').strip() or None,
                _parse_int(request.form.get('vintage')),
                request.form.get('sweetness', '').strip() or None,
                request.form.get('body', '').strip() or None,
                request.form.get('acidity', '').strip() or None,
            )

        flash(f'"{name}" updated.', 'success')
        return redirect(url_for('admin_products'))

    # GET — load product and build form dict
    product = repo.find(product_id)
    if product is None:
        return render_template('404.html'), 404
    if product.category == 'wine':
        product = repo.find_wine(product_id)

    form_data = {
        'name': product.name or '',
        'category': product.category or '',
        'subcategory': product.subcategory or '',
        'description': product.description or '',
        'producer': product.producer or '',
        'country': product.country or '',
        'abv': str(product.abv) if product.abv is not None else '',
        'vegan': 'on' if product.vegan else '',
        'organic': 'on' if product.organic else '',
        'region': product.region or '',
        'vintage': str(product.vintage) if product.vintage is not None else '',
        'sweetness': product.sweetness or '',
        'body': product.body or '',
        'acidity': product.acidity or '',
    }
    return render_template('admin/product_form.html', product=product, form=form_data)


@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
def admin_product_delete(product_id):
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)
    product = repo.find(product_id)
    if product:
        repo.delete_product(product_id)
        flash(f'"{product.name}" deleted.', 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/<int:product_id>/variants')
@login_required
def admin_product_variants(product_id):
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)
    product = repo.find(product_id)
    if product is None:
        return render_template('404.html'), 404
    variants = repo.product_variants(product_id)
    return render_template('admin/variants.html', product=product, variants=variants)


@app.route('/admin/products/<int:product_id>/variants/new', methods=['POST'])
@login_required
def admin_variant_create(product_id):
    serve_label = request.form.get('serve_label', '').strip().title()
    price = _parse_decimal(request.form.get('price'))
    serve_ml = _parse_int(request.form.get('serve_ml'))
    sort_order = _parse_int(request.form.get('sort_order')) or 1

    if not serve_label or price is None:
        flash('Serve label and price are required.', 'error')
    else:
        connection = get_flask_database_connection(app)
        repo = ProductRepository(connection)
        repo.create_variant(product_id, serve_label, serve_ml, price, sort_order)
        flash('Variant added.', 'success')
    return redirect(url_for('admin_product_variants', product_id=product_id))


@app.route('/admin/variants/<int:variant_id>/edit', methods=['POST'])
@login_required
def admin_variant_update(variant_id):
    product_id = _parse_int(request.form.get('product_id'))
    serve_label = request.form.get('serve_label', '').strip().title()
    price = _parse_decimal(request.form.get('price'))
    serve_ml = _parse_int(request.form.get('serve_ml'))
    sort_order = _parse_int(request.form.get('sort_order')) or 1

    if not serve_label or price is None:
        flash('Serve label and price are required.', 'error')
    else:
        connection = get_flask_database_connection(app)
        repo = ProductRepository(connection)
        repo.update_variant(variant_id, serve_label, serve_ml, price, sort_order)
        flash('Variant updated.', 'success')
    return redirect(url_for('admin_product_variants', product_id=product_id))


@app.route('/admin/variants/<int:variant_id>/delete', methods=['POST'])
@login_required
def admin_variant_delete(variant_id):
    product_id = _parse_int(request.form.get('product_id'))
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)
    repo.delete_variant(variant_id)
    flash('Variant deleted.', 'success')
    return redirect(url_for('admin_product_variants', product_id=product_id))


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
