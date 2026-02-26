class ProductVariant:

    def __init__(self, id, product_id, serve_label, serve_ml, price, sort_order):
        self.id = id
        self.product_id = product_id
        self.serve_label = serve_label
        self.serve_ml = serve_ml
        self.price = price
        self.sort_order = sort_order
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __repr__(self):
        return f"""ProductVariant(
    {self.id},
    {self.product_id},
    {self.serve_label},
    {self.serve_ml},
    {self.price},
    {self.sort_order})"""