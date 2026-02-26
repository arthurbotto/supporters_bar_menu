class Product:

    def __init__(
            self, 
            id, 
            section_id, 
            code, 
            name, 
            category, 
            subcategory, 
            description, 
            producer, 
            country, 
            abv, 
            vegan, 
            organic,
            region,
            vintage):
        
        self.id = id
        self.section_id = section_id
        self.code = code
        self.name = name
        self.category = category
        self.subcategory = subcategory
        self.description = description
        self.producer = producer
        self.country = country
        self.abv = abv
        self.vegan = vegan
        self.organic = organic
        self.region = region
        self.vintage = vintage
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __repr__(self):
        return f"""Product(
        {self.id},
        {self.section_id},
        {self.code},
        {self.name},
        {self.category},
        {self.subcategory},
        {self.description},
        {self.producer},
        {self.country},
        {self.abv},
        {self.vegan},
        {self.organic},
        {self.region},
        {self.vintage}
        )"""
        