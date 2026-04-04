from datetime import timedelta
import os
import uuid
from decimal import Decimal, InvalidOperation
from functools import wraps
from flask import Flask, redirect, request, render_template, url_for, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from psycopg.errors import UniqueViolation
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image as PilImage
from lib.admin_log_repository import AdminLogRepository
from lib.database_connection import get_flask_database_connection
from lib.cocktail_repository import CocktailRepository
from lib.ingredient_repository import IngredientRepository
from lib.product import Product
from lib.product_repository import ProductRepository
from lib.product_code import make_product_code
from lib.recipe_item_repository import RecipeItemRepository

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-fallback-change-me')
app.config['WTF_CSRF_ENABLED'] = True
app.config['RATELIMIT_ENABLED'] = os.getenv('APP_ENV') != 'test'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
_WINE_MAX_DIM = 1200
_IMG_MAX_DIM = 1200

def _save_image(file, subfolder: str = '') -> str | None:
    """Normalise and save uploaded image to static/images/{subfolder}/. Returns relative path or None."""
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    folder = os.path.join(app.config['UPLOAD_FOLDER'], subfolder) if subfolder else app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    stem = secure_filename(file.filename).rsplit('.', 1)[0]
    filename = f"{uuid.uuid4().hex[:12]}_{stem}.jpg"
    save_path = os.path.join(folder, filename)
    max_dim = _WINE_MAX_DIM if subfolder == 'wine' else _IMG_MAX_DIM
    img = PilImage.open(file.stream).convert('RGB')
    if subfolder == 'wine':
        w, h = img.size
        if h > w * 1.8:
            target_w = int(h / 1.5)
            canvas = PilImage.new('RGB', (target_w, h), (248, 248, 248))
            canvas.paste(img, ((target_w - w) // 2, 0))
            img = canvas
    elif subfolder == 'cocktails':
        w, h = img.size
        if h > w * 1.3:  # portrait — pad sides to square
            canvas = PilImage.new('RGB', (h, h), (243, 244, 246))
            canvas.paste(img, ((h - w) // 2, 0))
            img = canvas
    img.thumbnail((max_dim, max_dim), PilImage.Resampling.LANCZOS)
    img.save(save_path, format='JPEG', quality=88, optimize=True)
    return f"images/{subfolder}/{filename}" if subfolder else f"images/{filename}"

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

def _parse_bool(value):
    v = (value or "").strip().lower()
    if v == "":
        return None
    if v in ("true", "t", "1", "yes", "y"):
        return True
    if v in ("false", "f", "0", "no", "n"):
        return False
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
    connection = get_flask_database_connection(app)
    ing_repo = IngredientRepository(connection)
    spirits = ing_repo.spirit_types()

    return render_template('cocktails.html', spirits=spirits)




@app.route('/cocktails/<int:cocktail_id>/modal')
def cocktail_modal(cocktail_id):
    connection = get_flask_database_connection(app)
    cocktail_repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)

    cocktail = cocktail_repo.find_cocktail(cocktail_id)
    if cocktail is None:
        return render_template('404.html'), 404

    cocktail.recipe_items = recipe_repo.for_cocktail(cocktail.id)

    return render_template("cocktail_modal.html", cocktail=cocktail)

@app.route('/search_cocktails')
def search_cocktails():
    q = request.args.get('q', '').strip()
    spirit_type = request.args.get('spirit_type', '').strip()

    connection = get_flask_database_connection(app)
    cocktail_repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)

    
    cocktails = cocktail_repo.search_cocktail(query=q, spirit_type=spirit_type)
    
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

# ---------------
# snacks page
# ---------------

@app.route('/snacks')
def get_snacks_page():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    snacks = product_repo.all_snacks()

    for snack in snacks:
        snack.variants = product_repo.product_variants(snack.id)
    
    return render_template('snacks.html', snacks=snacks)




# ===========================
# Admin routes
# ===========================

@app.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
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
            session.permanent = True
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

@app.route('/admin/logs')
@login_required
def admin_logs_all():
    connection = get_flask_database_connection(app)
    log_repo = AdminLogRepository(connection)
    logs = log_repo.all_logs()
    return render_template('admin/logs.html', logs=logs)

# --------------------
# ADMIN PRODUCT ROUTES
# --------------------

@app.route('/admin/products')
@login_required
def admin_products():
    return render_template('admin/products.html')

@app.route('/admin/search_products')
@login_required
def admin_search_products():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)

    products = repo.search_product(q, category)
    
    return render_template('admin/products_list.html', products=products)


@app.route('/admin/products/<int:product_id>/toggle', methods=['POST'])
@login_required
def admin_toggle_active(product_id):
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)
    log_repo = AdminLogRepository(connection)
    product = repo.find(product_id)
    if product is None:
        flash('Product not found.', 'error')
    else:
        repo.set_active(product_id, not product.is_active)
        status = 'active' if not product.is_active else 'inactive'
        log_repo.log('toggle', 'product', product_id, product.name, detail=status)
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
        image_url = _save_image(request.files.get('image'), category)

        connection = get_flask_database_connection(app)
        repo = ProductRepository(connection)
        product_id = repo.create_product(
            code, name, category, subcategory, description, producer, country, abv, vegan, organic, image_url
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

        log_repo = AdminLogRepository(connection)
        log_repo.log('create', 'product', product_id, name, detail=category)
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
        image_url = _save_image(request.files.get('image'), category)
        if image_url is None:
            existing = repo.find(product_id)
            image_url = existing.image_url if existing else None

        repo.update_product(
            product_id, name, category, subcategory, description, producer, country, abv, vegan, organic, image_url
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

        log_repo = AdminLogRepository(connection)
        log_repo.log('update', 'product', product_id, name, detail='updated')
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
        log_repo = AdminLogRepository(connection)
        log_repo.log('delete', 'product', product_id, product.name, detail=product.category)
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
        product = repo.find(product_id)
        log_repo = AdminLogRepository(connection)
        log_repo.log('create', 'variant', product_id, product.name if product else None, detail=f'{serve_label} · £{price}')
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
        product = repo.find(product_id)
        log_repo = AdminLogRepository(connection)
        log_repo.log('update', 'variant', product_id, product.name if product else None, detail=f'{serve_label} · £{price}')
        flash('Variant updated.', 'success')
    return redirect(url_for('admin_product_variants', product_id=product_id))


@app.route('/admin/variants/<int:variant_id>/delete', methods=['POST'])
@login_required
def admin_variant_delete(variant_id):
    product_id = _parse_int(request.form.get('product_id'))
    serve_label = request.form.get('serve_label', '').strip()
    connection = get_flask_database_connection(app)
    repo = ProductRepository(connection)
    product = repo.find(product_id)
    repo.delete_variant(variant_id)
    log_repo = AdminLogRepository(connection)
    log_repo.log('delete', 'variant', product_id, product.name if product else None, detail=serve_label or None)
    flash('Variant deleted.', 'success')
    return redirect(url_for('admin_product_variants', product_id=product_id))


# ---------------------
# ADMIN COCKTAIL ROUTES
# ---------------------

@app.route('/admin/cocktails')
@login_required
def admin_cocktails():
    return render_template('admin/cocktails.html')

@app.route('/admin/search_cocktails')
@login_required
def admin_search_cocktails():
    q = request.args.get('q', '').strip()
    connection = get_flask_database_connection(app)
    repo = CocktailRepository(connection)

    if q == '':
        cocktails = repo.all_cocktails_for_admin()
    else:
        cocktails = repo.search_cocktail_admin(q)
    
    return render_template('admin/cocktails_list.html', cocktails=cocktails)

@app.route('/admin/cocktails/<int:cocktail_id>/toggle', methods=['POST'])
@login_required
def admin_toggle_active_cocktail(cocktail_id):
    connection = get_flask_database_connection(app)
    repo = CocktailRepository(connection)
    cocktail = repo.find_cocktail(cocktail_id)
    if cocktail is None:
        flash('Cocktail no found.', 'error')
    else:
        repo.set_active(cocktail_id, not cocktail.is_active)
        status = 'active' if not cocktail.is_active else 'inactive'
        log_repo = AdminLogRepository(connection)
        log_repo.log('toggle', 'cocktail', cocktail_id, cocktail.name, detail=status)
        flash(f'"{cocktail.name}" set to {status}.', 'success')
    return redirect(url_for('admin_cocktails'))

@app.route('/admin/cocktails/new', methods=['GET', 'POST'])
@login_required
def admin_cocktail_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        subcategory = request.form.get('subcategory', '').strip()
        if not name or not subcategory:
            flash('Name and subcategory are required.', 'error')
            return render_template('admin/cocktail_form.html', cocktail=None, form=request.form)
        description = request.form.get('description', '').strip() or None
        history = request.form.get('history', '').strip() or None
        method = request.form.get('method', '').strip() or None
        glass = request.form.get('glass', '').strip() or None
        garnish = request.form.get('garnish', '').strip() or None
        abv = _parse_decimal(request.form.get('abv', ''))
        price = _parse_decimal(request.form.get('price', ''))
        image_url = _save_image(request.files.get('image'), 'cocktails')

        connection = get_flask_database_connection(app)
        repo = CocktailRepository(connection)
        try:
            cocktail_id = repo.create_cocktail(
                name, subcategory, description, history, method, glass, garnish, abv, price, image_url
            )
        except UniqueViolation:
            flash(f'A cocktail named "{name}" already exists.', 'error')
            return render_template('admin/cocktail_form.html', cocktail=None, form=request.form)

        log_repo = AdminLogRepository(connection)
        log_repo.log('create', 'cocktail', cocktail_id, name, detail=subcategory)
        flash(f'"{name}" created.', 'success')
        return redirect(url_for('admin_cocktail_recipe', cocktail_id=cocktail_id))

    return render_template('admin/cocktail_form.html', cocktail=None, form={})

@app.route('/admin/cocktails/<int:cocktail_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_cocktail_edit(cocktail_id):
    connection = get_flask_database_connection(app)
    repo = CocktailRepository(connection)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        subcategory = request.form.get('subcategory', '').strip()
        if not name or not subcategory:
            flash('Name and subcategory are required.', 'error')
            cocktail = repo.find_cocktail(cocktail_id)
            return render_template('admin/cocktail_form.html', cocktail=cocktail, form=request.form)
        description = request.form.get('description', '').strip() or None
        history = request.form.get('history', '').strip() or None
        method = request.form.get('method', '').strip() or None
        glass = request.form.get('glass', '').strip() or None
        garnish = request.form.get('garnish', '').strip() or None
        abv = _parse_decimal(request.form.get('abv', ''))
        price = _parse_decimal(request.form.get('price', ''))
        image_url = _save_image(request.files.get('image'), 'cocktails')
        if image_url is None:
            existing = repo.find_cocktail(cocktail_id)
            image_url = existing.image_url if existing else None

        try:
            repo.update_cocktail(
                cocktail_id, name, subcategory, description, history, method, glass, garnish, abv, price, image_url
            )
        except UniqueViolation:
            flash(f'A cocktail named "{name}" already exists.', 'error')
            cocktail = repo.find_cocktail(cocktail_id)
            return render_template('admin/cocktail_form.html', cocktail=cocktail, form=request.form)

        log_repo = AdminLogRepository(connection)
        log_repo.log('update', 'cocktail', cocktail_id, name, detail='updated')
        flash(f'"{name}" updated.', 'success')
        return redirect(url_for('admin_cocktails'))
    
    # GET - load cocktail and build form dict
    cocktail = repo.find_cocktail(cocktail_id)
    if cocktail is None:
        return render_template('404.html'), 404
    
    form_data = {
        'name': cocktail.name or '',
        'subcategory': cocktail.subcategory or '',
        'description': cocktail.description or '',
        'history': cocktail.history or '',
        'method': cocktail.method or '',
        'glass': cocktail.glass or '',
        'garnish': cocktail.garnish or '',
        'abv': str(cocktail.abv) if cocktail.abv is not None else '',
        'price': str(cocktail.price) if cocktail.price is not None else '', 
    }
    return render_template('admin/cocktail_form.html', cocktail=cocktail, form=form_data)

@app.route('/admin/cocktails/<int:cocktail_id>/delete', methods=['POST'])
@login_required
def admin_cocktail_delete(cocktail_id):
    connection = get_flask_database_connection(app)
    repo = CocktailRepository(connection)
    cocktail = repo.find_cocktail(cocktail_id)
    if cocktail:
        repo.delete_cocktail(cocktail_id)
        log_repo = AdminLogRepository(connection)
        log_repo.log('delete', 'cocktail', cocktail_id, cocktail.name, detail=cocktail.subcategory)
        flash(f'"{cocktail.name}" deleted.', 'success')
    return redirect(url_for('admin_cocktails'))

@app.route('/admin/cocktails/<int:cocktail_id>/recipe')
@login_required
def admin_cocktail_recipe(cocktail_id):
    connection = get_flask_database_connection(app)
    repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)
    cocktail = repo.find_cocktail(cocktail_id)
    if cocktail is None:
        return render_template('404.html'), 404
    recipe = recipe_repo.for_cocktail(cocktail_id)
    return render_template('admin/recipe.html', cocktail=cocktail, recipe=recipe)

@app.route('/admin/cocktails/<int:cocktail_id>/recipe/new', methods=['POST'])
@login_required
def admin_recipe_create(cocktail_id):
    ingredient_name = request.form.get('ingredient_name', '').strip().title()
    ingredient_category = request.form.get('ingredient_category', '').strip() or None
    ingredient_subcategory = request.form.get('ingredient_subcategory', '').strip() or None
    amount = _parse_decimal(request.form.get('amount'))
    unit = request.form.get('unit', '').strip()
    sort_order = _parse_int(request.form.get('sort_order')) or 1
    optional = _parse_bool(request.form.get('optional')) or False

    connection = get_flask_database_connection(app)
    i_repo = IngredientRepository(connection)
    r_repo = RecipeItemRepository(connection)

    ingredient = i_repo.find_ingredient_by_name(ingredient_name)
    if ingredient is None:
        ingredient_id = i_repo.create_ingredient(ingredient_name, ingredient_category, ingredient_subcategory)
    else:
        ingredient_id = ingredient.id

    r_repo.create_recipe(cocktail_id, ingredient_id, amount, unit, sort_order, optional)
    cocktail = CocktailRepository(connection).find_cocktail(cocktail_id)
    log_repo = AdminLogRepository(connection)
    log_repo.log('add ingredient', 'cocktail', cocktail_id, cocktail.name if cocktail else None, detail=ingredient_name)
    flash('Recipe item added.', 'success')
    return redirect(url_for('admin_cocktail_recipe', cocktail_id=cocktail_id))


@app.route('/admin/recipe/<int:recipe_id>/edit', methods=['POST'])
@login_required
def admin_recipe_update(recipe_id):
    cocktail_id = _parse_int(request.form.get('cocktail_id'))
    new_name = request.form.get('ingredient_name', '').strip().title()
    amount = _parse_decimal(request.form.get('amount'))
    unit = request.form.get('unit', '').strip()
    sort_order = _parse_int(request.form.get('sort_order')) or 1
    optional = _parse_bool(request.form.get('optional')) or False

    connection = get_flask_database_connection(app)
    i_repo = IngredientRepository(connection)
    r_repo = RecipeItemRepository(connection)

    ingredient = i_repo.find_ingredient_by_name(new_name)
    if ingredient is None:
        ingredient_id = i_repo.create_ingredient(new_name, None, None)
    else:
        ingredient_id = ingredient.id

    r_repo.update_recipe(recipe_id, ingredient_id, amount, unit, sort_order, optional)
    cocktail = CocktailRepository(connection).find_cocktail(cocktail_id)
    log_repo = AdminLogRepository(connection)
    log_repo.log('update ingredient', 'cocktail', cocktail_id, cocktail.name if cocktail else None, detail=new_name)
    flash('Recipe updated.', 'success')
    return redirect(url_for('admin_cocktail_recipe', cocktail_id=cocktail_id))


@app.route('/admin/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
def admin_recipe_delete(recipe_id):
    cocktail_id = _parse_int(request.form.get('cocktail_id'))
    ingredient_name = request.form.get('ingredient_name', '').strip()
    connection = get_flask_database_connection(app)
    r_repo = RecipeItemRepository(connection)
    cocktail = CocktailRepository(connection).find_cocktail(cocktail_id)
    r_repo.delete_recipe(recipe_id)
    log_repo = AdminLogRepository(connection)
    log_repo.log('remove ingredient', 'cocktail', cocktail_id, cocktail.name if cocktail else None, detail=ingredient_name or None)
    flash('Ingredient removed from recipe.', 'success')
    return redirect(url_for('admin_cocktail_recipe', cocktail_id=cocktail_id))

    





@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
