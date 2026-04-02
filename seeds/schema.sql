-- =========================================
-- Supporters House Bar Menu - schema.sql
-- PostgreSQL
-- =========================================

-- Drop in dependency order
DROP TABLE IF EXISTS recipe_items;
DROP TABLE IF EXISTS product_variants;
DROP TABLE IF EXISTS wine_details;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS cocktails;


CREATE TABLE cocktails (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subcategory TEXT,
    description TEXT,
    history TEXT,
    method VARCHAR(50),
    glass VARCHAR(50),
    garnish VARCHAR(255),
    abv NUMERIC(5,2),
    price NUMERIC(8,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    image_url VARCHAR(500)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cocktails_name_unique ON cocktails (name);

CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    subcategory VARCHAR(50)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ingredients_name_unique ON ingredients (name);
CREATE INDEX IF NOT EXISTS idx_ingredients_category ON ingredients (category);

CREATE TABLE recipe_items (
    id SERIAL PRIMARY KEY,
    cocktail_id INTEGER NOT NULL REFERENCES cocktails(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    amount NUMERIC(6,2),
    unit VARCHAR(50),
    sort_order INTEGER NOT NULL DEFAULT 1,
    optional BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_recipe_items_cocktail_id ON recipe_items (cocktail_id);
CREATE INDEX IF NOT EXISTS idx_recipe_items_ingredient_id ON recipe_items (ingredient_id);
CREATE INDEX IF NOT EXISTS idx_recipe_items_sort ON recipe_items (cocktail_id, sort_order);

CREATE UNIQUE INDEX IF NOT EXISTS idx_recipe_items_unique_line
ON recipe_items (cocktail_id, ingredient_id, sort_order);

-- =========================================
-- FULL MENU PRODUCTS
-- Base table + wine_details
-- =========================================

-- Base product (shared fields only)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,

    -- Stable unique identifier for imports + references
    -- (Importer auto-generates it if CSV doesn't provide one)
    code VARCHAR(180) NOT NULL,

    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,      -- 'spirit','wine','beer','soft','juice','hot','mocktail'
    subcategory VARCHAR(50),            -- 'gin','vodka','lager','red','white', etc.

    description TEXT,
    producer VARCHAR(255),
    country VARCHAR(255),

    abv NUMERIC(5,2),

    vegan BOOLEAN,
    organic BOOLEAN,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    image_url VARCHAR(500)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_products_code_unique ON products (code);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_subcategory ON products (subcategory);
-- Wine-only fields live here
CREATE TABLE wine_details (
    product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    region VARCHAR(255),
    vintage INTEGER,
    sweetness VARCHAR(50),
    body VARCHAR(50),
    acidity VARCHAR(50)
    -- grapes TEXT -- (add later maybe)
);

CREATE INDEX IF NOT EXISTS idx_wine_details_vintage ON wine_details (vintage);

-- Variants
CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,

    serve_label VARCHAR(50) NOT NULL,
    serve_ml INTEGER,

    price NUMERIC(8,2) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_product_variants_product_id ON product_variants (product_id);
CREATE INDEX IF NOT EXISTS idx_product_variants_sort ON product_variants (product_id, sort_order);

CREATE UNIQUE INDEX IF NOT EXISTS idx_product_variants_unique
ON product_variants (product_id, serve_label, serve_ml);

CREATE TABLE admin_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,         
    entity_name VARCHAR(255),
    detail TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
