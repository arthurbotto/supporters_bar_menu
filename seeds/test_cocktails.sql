-- Test seed for cocktail repository tests.
-- Requires seeds/schema.sql to have been run first to create tables.

INSERT INTO cocktails (name, description, history, method, glass, garnish, abv, price) VALUES
  ('Negroni',   'Bitter Italian classic',      'Invented in Florence', 'Stirred', 'Rocks',    'Orange peel', 24,  9.50),
  ('Mojito',    'Refreshing Cuban highball',   'Cuban origin',         'Muddled', 'Highball', 'Mint sprig',  12,  8.50),
  ('Margarita', 'Tart and tangy tequila sour', 'Mexican origin',       'Shaken',  'Coupe',    'Salt rim',    20,  9.00);

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
  (1, 1, 30, 'ml', 1),
  (1, 2, 30, 'ml', 2),
  (1, 3, 30, 'ml', 3),
  (2, 4, 50, 'ml', 1),
  (2, 5, 25, 'ml', 2),
  (2, 6, 15, 'ml', 3),
  (3, 7, 50, 'ml', 1),
  (3, 8, 25, 'ml', 2),
  (3, 5, 25, 'ml', 3);
