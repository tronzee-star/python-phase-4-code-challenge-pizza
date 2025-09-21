from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    pizzas = db.relationship("RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan")

    def to_dict(self, only=None, include_relations=False):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
        }

        if only:
            data = {field: data[field] for field in only if field in data}

        if include_relations:
            data["restaurant_pizzas"] = [rp.to_dict() for rp in self.pizzas]

        return data


class Pizza(db.Model):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurants = db.relationship("RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan")

    def to_dict(self, only=None):
        data = {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients,
        }

        if only:
            data = {field: data[field] for field in only if field in data}

        return data


class RestaurantPizza(db.Model):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))

    pizza = db.relationship("Pizza", back_populates="restaurants")
    restaurant = db.relationship("Restaurant", back_populates="pizzas")

    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
        }
