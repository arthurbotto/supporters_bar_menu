class Cocktail:

    def __init__(self, id, name, subcategory, description, history, method, glass, garnish, abv, price):
        self.id = id
        self.name = name
        self.subcategory = subcategory
        self.description = description
        self.history = history
        self.method = method
        self.glass = glass
        self.garnish = garnish
        self.abv = abv
        self.price = price
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __repr__(self):
        return f"""Cocktail(
    {self.id}, 
    {self.name},
    {self.subcategory},
    {self.description},
    {self.history}, 
    {self.method}, {self.glass}, 
    {self.garnish},
    {self.abv},
    {self.price})"""