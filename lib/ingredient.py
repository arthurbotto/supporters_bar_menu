class Ingredient:

    def __init__(self, id, name, category, subcategory):
        self.id = id
        self.name = name
        self.category = category
        self.subcategory = subcategory

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __repr__(self):
        return f'Ingredient({self.id}, {self.name}, {self.category}, {self.subcategory})'