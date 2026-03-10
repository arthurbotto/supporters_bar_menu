import os
from flask import Flask, redirect, request, render_template, url_for
from lib.database_connection import get_flask_database_connection
from lib.cocktail_repository import CocktailRepository
from lib.product import Product
from lib.product_repository import ProductRepository
from lib.recipe_item_repository import RecipeItemRepository

app = Flask(__name__)



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
        spirit_list.sort(key=lambda s: min(s.price_by_ml.values()))
    
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
    return render_template('wines.html')
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
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)

    if q == '':
        wines = product_repo.all_wines()
    else:
        wines = product_repo.search_wine(q)
    
    grouped = {}
    section_sizes = {}

    for wine in wines:
        wine.variants = product_repo.product_variants(wine.id)
        wine.price_by_ml = {v.serve_ml: v.price for v in wine.variants}
        if wine.subcategory not in grouped:
            grouped[wine.subcategory] = []
            section_sizes[wine.subcategory] = set()
        grouped[wine.subcategory].append(wine)
        for ml in wine.price_by_ml:
            section_sizes[wine.subcategory].add(ml)

    section_sizes = {k: sorted(v) for k, v in section_sizes.items()}

    for wines_list in grouped.values():
        wines_list.sort(key=lambda w: min(w.price_by_ml.values()))

    section_order = ['red', 'white', 'rose', 'sparkling', 'dessert']

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


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
