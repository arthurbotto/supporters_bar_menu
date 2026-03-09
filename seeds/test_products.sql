-- =========================================
-- Test seed data for ProductRepository tests
-- Run after schema.sql (which drops/recreates all tables)
-- section_id is nullable — all rows use NULL
-- =========================================

-- Products
INSERT INTO products (section_id, code, name, category, subcategory, description, producer, country, abv, vegan, organic) VALUES
  (NULL, 'WINE-001',   'Malbec Reserva',          'wine',     'red',       'Plum and spice',    'Catena',      'Argentina',     13.5, TRUE, NULL),
  (NULL, 'WINE-002',   'Rioja Crianza',           'wine',     'red',       'Cherry and vanilla','Muga',        'Spain',         13.0, NULL, NULL),
  (NULL, 'WINE-003',   'Sauvignon Blanc',         'wine',     'white',     'Crisp and citrus',  'Featherdrop', 'New Zealand',   12.5, NULL, NULL),
  (NULL, 'WINE-004',   'Prosecco',                'wine',     'sparkling', 'Light and bubbly',  'Bisol',       'Italy',         11.0, TRUE, NULL),
  (NULL, 'SPIRIT-001', 'Hendricks Gin',           'spirit',   'gin',       NULL,                'Hendrick''s', 'Scotland',      41.4, NULL, NULL),
  (NULL, 'SPIRIT-002', 'Grey Goose',              'spirit',   'vodka',     NULL,                'Grey Goose',  'France',        40.0, NULL, NULL),
  (NULL, 'BEER-001',   'Camden Hells',            'beer',     NULL,        NULL,                'Camden Town', 'England',        4.6, NULL, NULL),
  (NULL, 'BEER-002',   'Guinness',                'beer',     NULL,        NULL,                'Guinness',    'Ireland',        4.1, NULL, NULL),
  (NULL, 'SOFT-001',   'Coca-Cola',               'soft',     'classic',   NULL,                NULL,          NULL,            NULL, NULL, NULL),
  (NULL, 'SOFT-002',   'Orange Juice',            'soft',    'juice',        NULL,                NULL,          NULL,            NULL, NULL, NULL),
  (NULL, 'HOT-001',    'Espresso',                'hot',      'coffee',    NULL,                NULL,          NULL,            NULL, NULL, NULL),
  (NULL, 'HOT-002',    'English Breakfast Tea',   'hot',      'tea',       NULL,                NULL,          NULL,            NULL, NULL, NULL),
  (NULL, 'MOCK-001',   'Virgin Mojito',           'mocktail', NULL,        'Mint and lime',     NULL,          NULL,               0, NULL, NULL),
  (NULL, 'MOCK-002',   'Shirley Temple',          'mocktail', NULL,        'Ginger and cherry', NULL,          NULL,               0, NULL, NULL);

-- Wine details (wines only)
INSERT INTO wine_details (product_id, region, vintage) VALUES
  ((SELECT id FROM products WHERE code = 'WINE-001'), 'Mendoza',     2021),
  ((SELECT id FROM products WHERE code = 'WINE-002'), 'Rioja',       2020),
  ((SELECT id FROM products WHERE code = 'WINE-003'), 'Marlborough', 2023),
  ((SELECT id FROM products WHERE code = 'WINE-004'), 'Veneto',      NULL);

-- Product variants
-- Wines: 125ml (sort 1) and 175ml (sort 2)
INSERT INTO product_variants (product_id, serve_label, serve_ml, price, sort_order) VALUES
  ((SELECT id FROM products WHERE code = 'WINE-001'), '125ml', 125, 6.50, 1),
  ((SELECT id FROM products WHERE code = 'WINE-001'), '175ml', 175, 8.50, 2),
  ((SELECT id FROM products WHERE code = 'WINE-002'), '125ml', 125, 6.00, 1),
  ((SELECT id FROM products WHERE code = 'WINE-002'), '175ml', 175, 8.00, 2),
  ((SELECT id FROM products WHERE code = 'WINE-003'), '125ml', 125, 6.50, 1),
  ((SELECT id FROM products WHERE code = 'WINE-003'), '175ml', 175, 8.50, 2),
  ((SELECT id FROM products WHERE code = 'WINE-004'), '125ml', 125, 7.00, 1),
  ((SELECT id FROM products WHERE code = 'WINE-004'), '175ml', 175, 9.00, 2);

-- Spirits: 50ml only
INSERT INTO product_variants (product_id, serve_label, serve_ml, price, sort_order) VALUES
  ((SELECT id FROM products WHERE code = 'SPIRIT-001'), '50ml', 50, 9.00, 1),
  ((SELECT id FROM products WHERE code = 'SPIRIT-002'), '50ml', 50, 9.50, 1);

-- Beers: pint only
INSERT INTO product_variants (product_id, serve_label, serve_ml, price, sort_order) VALUES
  ((SELECT id FROM products WHERE code = 'BEER-001'), 'Pint', 568, 5.50, 1),
  ((SELECT id FROM products WHERE code = 'BEER-002'), 'Pint', 568, 5.80, 1);

-- Softs: glass
INSERT INTO product_variants (product_id, serve_label, serve_ml, price, sort_order) VALUES
  ((SELECT id FROM products WHERE code = 'SOFT-001'), 'Glass', 330, 2.50, 1),
  ((SELECT id FROM products WHERE code = 'SOFT-002'), 'Glass', 250, 3.00, 1);

-- Hot drinks: cup
INSERT INTO product_variants (product_id, serve_label, serve_ml, price, sort_order) VALUES
  ((SELECT id FROM products WHERE code = 'HOT-001'), 'Cup', NULL, 2.50, 1),
  ((SELECT id FROM products WHERE code = 'HOT-002'), 'Cup', NULL, 2.50, 1);

-- Mocktails: glass
INSERT INTO product_variants (product_id, serve_label, serve_ml, price, sort_order) VALUES
  ((SELECT id FROM products WHERE code = 'MOCK-001'), 'Glass', NULL, 6.00, 1),
  ((SELECT id FROM products WHERE code = 'MOCK-002'), 'Glass', NULL, 6.00, 1);
