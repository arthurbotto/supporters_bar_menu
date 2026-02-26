class RecipeItem:

    def __init__(
            self,
            id,
            cocktail_id,
            ingredient_id,
            amount,
            unit,
            sort_order,
            optional,
            ingredient_name=None,
            ingredient_category=None
    ):
        self.id = id
        self.cocktail_id = cocktail_id
        self.ingredient_id = ingredient_id
        self.amount = amount
        self.unit = unit
        self.sort_order = sort_order
        self.optional = optional
        self.ingredient_name = ingredient_name
        self.ingredient_category = ingredient_category
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __repr__(self):
        return f'''RecipeItem(
        {self.id} 
        {self.cocktail_id}
        {self.ingredient_id}
        {self.amount}
        {self.unit}
        {self.sort_order}
        {self.optional}
        {self.ingredient_name}
        {self.ingredient_category}
        )'''