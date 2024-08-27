#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict() for r in restaurants]

class RestaurantDetail(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return {
                **restaurant.to_dict(),
                "restaurant_pizzas": [rp.to_dict() for rp in restaurant.restaurant_pizzas]
            }
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            RestaurantPizza.query.filter_by(restaurant_id=id).delete()
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        return {"error": "Restaurant not found"}, 404

class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict() for p in pizzas]

class RestaurantPizzaCreate(Resource):
    def post(self):
        data = request.get_json()
        try:
            pizza = Pizza.query.get(data['pizza_id'])
            restaurant = Restaurant.query.get(data['restaurant_id'])
            if not pizza or not restaurant:
                raise ValueError("Invalid pizza or restaurant ID")

            restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return {
                **restaurant_pizza.to_dict(),
                "pizza": pizza.to_dict(),
                "restaurant": restaurant.to_dict()
            }, 201
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            return {"errors": ["internal server error"]}, 500


api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')
api.add_resource(RestaurantPizzaCreate, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)
