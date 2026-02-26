import os
from flask import Flask, redirect, request, render_template, url_for
from lib.database_connection import get_flask_database_connection
from lib.cocktail_repository import CocktailRepository
from lib.product_repository import ProductRepository
from lib.recipe_item_repository import RecipeItemRepository

app = Flask(__name__)




@app.route('/')
def get_home_page():
    return render_template('home.html')


@app.route('/products')
def get_products():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    products = product_repo.all()

    return render_template('products.html', products=products)


@app.route('/wines')
def get_wines():
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    wines = product_repo.all_wines()

    # Group wines by subcategory into a dictionary
    grouped = {}
    for wine in wines:
        wine.variants = product_repo.product_variants(wine.id)
        wine.price_by_ml = {v.serve_ml: v.price for v in wine.variants}
        if wine.subcategory not in grouped:
            grouped[wine.subcategory] = []
        grouped[wine.subcategory].append(wine)

    # Sort wines by price.
    for wines_list in grouped.values():
        wines_list.sort(key=lambda w: min(w.price_by_ml.values()))

    # Compute the distinct serve sizes present in each section (for column headers)
    section_sizes = {}
    for section, wines_list in grouped.items():
        sizes = set()
        for wine in wines_list:
            for ml in wine.price_by_ml:
                sizes.add(ml)
        section_sizes[section] = sorted(sizes)

    # The order that sections should appear in the page
    section_order = ['red', 'white', 'rose', 'sparkling', 'dessert']

    return render_template('wines.html', grouped=grouped, section_order=section_order, section_sizes=section_sizes)

@app.route('/wines/<int:wine_id>/modal')
def wine_modal(wine_id):
    connection = get_flask_database_connection(app)
    product_repo = ProductRepository(connection)
    
    wine = product_repo.find_wine(wine_id, "id")

    if wine is None:
        return "Not Found", 404

    return render_template("wine_modal.html", wine=wine)


@app.route('/cocktails')
def get_cocktails_page():
    connection = get_flask_database_connection(app)
    cocktail_repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)
    cocktails = cocktail_repo.all()
    

    for cocktail in cocktails:
        cocktail.recipe_items = recipe_repo.for_cocktail(cocktail.id)

    return render_template('cocktails.html', cocktails=cocktails)




@app.route('/cocktails/<int:cocktail_id>/modal')
def cocktail_modal(cocktail_id):
    connection = get_flask_database_connection(app)
    cocktail_repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)

    cocktail = cocktail_repo.find_cocktail(cocktail_id, "id")
    if cocktail is None:
        return "Not found", 404

    cocktail.recipe_items = recipe_repo.for_cocktail(cocktail.id)

    return render_template("cocktail_modal.html", cocktail=cocktail)

@app.route('/search')
def search_cocktails():
    q = request.args.get('q', '').strip()

    connection = get_flask_database_connection(app)
    cocktail_repo = CocktailRepository(connection)
    recipe_repo = RecipeItemRepository(connection)

    if q == '':
        cocktails = cocktail_repo.all()
    else:
        cocktails = cocktail_repo.search(q)
    
    for cocktail in cocktails:
        cocktail.recipe_items = recipe_repo.for_cocktail(cocktail.id)
    
    return render_template("cocktail_list.html", cocktails=cocktails)




















if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5001)))
