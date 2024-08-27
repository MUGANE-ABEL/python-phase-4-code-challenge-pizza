from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship with RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')

    # Serialization rules
    serialize_only = ('id', 'name', 'address')
    serialize_rules = ('-restaurant_pizzas.restaurant',)  # Exclude recursive relationships

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationship with RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza')

    # Serialization rules
    serialize_only = ('id', 'name', 'ingredients')
    serialize_rules = ('-restaurant_pizzas.pizza',)  # Exclude recursive relationships

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Relationships
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')

    # Serialization rules
    serialize_only = ('id', 'price', 'pizza_id', 'restaurant_id', 'pizza', 'restaurant')
    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas')  # Exclude recursive relationships

    @validates('price')
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
