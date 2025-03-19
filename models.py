from extensions import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric)

    inventories = db.relationship('Inventory', back_populates='product')

    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    inventories = db.relationship('Inventory', back_populates='location')
    def __init__(self, name):
        self.name = name


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    quantity = db.Column(db.Integer)
    product = db.relationship('Product', back_populates='inventories')
    location = db.relationship('Location', back_populates='inventories')

    def __init__(self, product_id, location_id, quantity):
        self.product_id = product_id
        self.location_id = location_id
        self.quantity = quantity