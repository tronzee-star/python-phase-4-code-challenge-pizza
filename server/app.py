#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
from flask_restful import Api
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# -----------------------------
# GET /restaurants
# -----------------------------
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = [r.to_dict(only=("id", "name", "address")) for r in Restaurant.query.all()]
    return jsonify(restaurants), 200


# -----------------------------
# GET /restaurants/<id>
# DELETE /restaurants/<id>
# -----------------------------
@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    if request.method == "GET":
        return jsonify(restaurant.to_dict(include_relations=True)), 200

    if request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204


# -----------------------------
# GET /pizzas
# -----------------------------
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = [p.to_dict(only=("id", "name", "ingredients")) for p in Pizza.query.all()]
    return jsonify(pizzas), 200

# -----------------------------
# POST /restaurant_pizzas
# -----------------------------
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        price = data["price"]
        pizza_id = data["pizza_id"]
        restaurant_id = data["restaurant_id"]

        new_rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_rp)
        db.session.commit()

        # ✅ reload so relationships are available
        db.session.refresh(new_rp)

        # ✅ build response with both pizza and restaurant
        response = {
            "id": new_rp.id,
            "price": new_rp.price,
            "pizza_id": new_rp.pizza_id,
            "restaurant_id": new_rp.restaurant_id,
            "pizza": new_rp.pizza.to_dict(only=("id", "name", "ingredients")),
            "restaurant": new_rp.restaurant.to_dict(only=("id", "name", "address")),
        }

        return jsonify(response), 201

    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

