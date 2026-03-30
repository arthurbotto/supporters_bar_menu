class Product:

    def __init__(
            self,
            id,
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
            is_active,
            region,
            vintage,
            sweetness,
            body,
            acidity,
            image_url):
        
        self.id = id
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
        self.is_active = is_active
        self.region = region
        self.vintage = vintage
        self.sweetness = sweetness
        self.body = body
        self.acidity = acidity
        self.variants = []
        self.price_by_ml = {}
        self.image_url = image_url
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __repr__(self):
        return f"""Product(
        {self.id},
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
        {self.is_active},
        {self.region},
        {self.vintage},
        {self.sweetness},
        {self.body},
        {self.acidity},
        {self.image_url}
        )"""
        