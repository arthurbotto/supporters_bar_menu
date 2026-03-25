var SUBCATEGORY_SUGGESTIONS = {
  spirit:   ['gin', 'vodka', 'rum', 'tequila', 'whisky', 'vermouth', 'liqueur', 'brandy'],
  beer:     ['lager', 'ale', 'stout', 'ipa', 'wheat', 'porter'],
  soft:     ['fever_tree', 'san_pellegrino', 'classic', 'juice', 'water'],
  hot:      ['coffee', 'tea'],
  mocktail: ['non_alcoholic_cocktail']
};

function toggleCategoryFields() {
  var cat = document.getElementById('category').value;
  var isWine = (cat === 'wine');

  // Wine-only section visibility
  document.getElementById('wine-fields').style.display = isWine ? 'block' : 'none';

  // Swap subcategory between <select> (wine) and <input list> (everything else)
  var wineSelect = document.getElementById('subcategory-wine');
  var textInput  = document.getElementById('subcategory-text');
  wineSelect.style.display = isWine ? '' : 'none';
  wineSelect.disabled      = !isWine;
  textInput.style.display  = isWine ? 'none' : '';
  textInput.disabled       = isWine;

  // Replace datalist options with suggestions for the selected category
  var datalist = document.getElementById('subcategory-options');
  var suggestions = SUBCATEGORY_SUGGESTIONS[cat] || [];
  datalist.innerHTML = suggestions.map(function(v) {
    return '<option value="' + v + '">';
  }).join('');
}

document.getElementById('category').addEventListener('change', toggleCategoryFields);
toggleCategoryFields(); // run on page load for edit pre-fill
