-- Test seed for cocktail repository tests.
-- Requires seeds/schema.sql to have been run first to create tables.

INSERT INTO cocktails (name, subcategory, description, history, method, glass, garnish, abv, price) VALUES
  ('Negroni', 'from_menu',   'Bitter Italian classic',      'Invented in Florence', 'Stirred', 'Rocks',    'Orange peel', 24,  9.50),
  ('Mojito', 'classic',    'Refreshing Cuban highball',   'Cuban origin',         'Muddled', 'Highball', 'Mint sprig',  12,  8.50),
  ('Margarita', 'classic', 'Tart and tangy tequila sour', 'Mexican origin',       'Shaken',  'Coupe',    'Salt rim',    20,  9.00);

INSERT INTO ingredients (name, category) VALUES
  ('Gin',            'spirit'),
  ('Campari',        'liqueur'),
  ('Sweet Vermouth', 'vermouth'),
  ('White Rum',      'spirit'),
  ('Lime Juice',     'juice'),
  ('Sugar Syrup',    'syrup'),
  ('Tequila',        'spirit'),
  ('Triple Sec',     'liqueur');

-- Negroni: Gin, Campari, Sweet Vermouth
-- Mojito: White Rum, Lime Juice, Sugar Syrup
-- Margarita: Tequila, Triple Sec, Lime Juice  (shares Lime Juice with Mojito)
INSERT INTO recipe_items (cocktail_id, ingredient_id, amount, unit, sort_order) VALUES
  ((SELECT id FROM cocktails WHERE name = 'Negroni'), (SELECT id FROM ingredients WHERE name = 'Gin'), 30, 'ml', 1),
  ((SELECT id FROM cocktails WHERE name = 'Negroni'), (SELECT id FROM ingredients WHERE name = 'Campari'), 30, 'ml', 2),
  ((SELECT id FROM cocktails WHERE name = 'Negroni'), (SELECT id FROM ingredients WHERE name = 'Sweet Vermouth'), 30, 'ml', 3),
  ((SELECT id FROM cocktails WHERE name = 'Mojito'), (SELECT id FROM ingredients WHERE name = 'White Rum'), 50, 'ml', 1),
  ((SELECT id FROM cocktails WHERE name = 'Mojito'), (SELECT id FROM ingredients WHERE name = 'Lime Juice'), 25, 'ml', 2),
  ((SELECT id FROM cocktails WHERE name = 'Mojito'), (SELECT id FROM ingredients WHERE name = 'Sugar Syrup'), 15, 'ml', 3),
  ((SELECT id FROM cocktails WHERE name = 'Margarita'), (SELECT id FROM ingredients WHERE name = 'Tequila'), 50, 'ml', 1),
  ((SELECT id FROM cocktails WHERE name = 'Margarita'), (SELECT id FROM ingredients WHERE name = 'Triple Sec'), 25, 'ml', 2),
  ((SELECT id FROM cocktails WHERE name = 'Margarita'), (SELECT id FROM ingredients WHERE name = 'Lime Juice'), 25, 'ml', 3);
