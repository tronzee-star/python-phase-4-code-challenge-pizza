# server/app.py (or add the following to your routes blueprint)
from flask import Flask, jsonify, request, abort
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
# ... existing config and db.init_app(app) ...

# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(include_restaurant_pizzas=False) for r in restaurants]), 200


# GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(restaurant.to_dict(include_restaurant_pizzas=True)), 200


# DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Because of cascade, deleting the restaurant should remove RestaurantPizza rows
    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict() for p in pizzas]), 200


# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    if not data:
        return jsonify({"errors": ["Invalid JSON data"]}), 400

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Ensure referenced pizza and restaurant exist
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    if not pizza or not restaurant:
        errors = []
        if not pizza:
            errors.append("Pizza not found")
        if not restaurant:
            errors.append("Restaurant not found")
        return jsonify({"errors": errors}), 404

    try:
        rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(rp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Extract validation message(s) if ValueError raised
        # Often the validate_price raises ValueError; return that as errors list.
        msg = str(e)
        # If it's a sqlalchemy IntegrityError or other, surface generic message
        return jsonify({"errors": [msg]}), 400

    # return the created object including nested pizza & restaurant
    rp = RestaurantPizza.query.get(rp.id)
    return jsonify(rp.to_dict()), 201
