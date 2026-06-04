from flask import Flask, jsonify, requests
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from ollama import Client
import os
load_dotenv()

app = Flask(__name__)

# create Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gaty.db"

# creating an object or instance
db = SQLAlchemy(app)
# creating a table
class Destination(db.Model):
    ID = db.Column(db.Integer, primary_key= True)
    destination = db.Column(db.String(50), nullable = False)
    country = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False)
# converting a database record into a python dictionary
    def to_dict(self):
        return {
            "ID" : self.ID,
            "destination" : self.destination,
            "country" : self.country,
            "rating" : self.rating

      }
with app.app_context():
    db.create_all()

#create routes
#https://www.thenerdnook.io/ (Home)
@app.route("/")
def home():
    return jsonify({"Greetings" : "Welcome to our Travel API"})

# https://www.thenerdnook.io/destinations
@app.route("/destinations", methods = ["GET"])
def get_destinations():
    destinations = Destination.query.all()
    return jsonify([destination.to_dict() for d in destinations])

# To get a specific destination, "id" is used
# https://www.thenerdnook.io/destinations/2
@app.route("/destinations/<int:destination_id>", methods = ["GET"])
def destination(destination_id):
    destination1 = db.session.get(destination_id, Destination)
    if destination1:
        return jsonify([destination1.to_dict()])
    else:
        return jsonify({"error" : "Destination not found!"}), 404

#POST
@app.route("/destinations", methods = ["POST"])
def add_destination():
    data = request.get_json()

    new_destination = Destination(
       destination=data["destination"],
       country=data["country"],
       rating=data["rating"]
     )

    db.session.add(new_destination)
    db.session.commit()

    return jsonify(new_destination.to_dict()), 201

# PUT = update
@app.route("/destinations/<int:destination_id>", methods=["PUT"])
def update_destination(destination_id):
    data = request.get_json()

    new_destination = db.session.get(destination_id, Destination)
    if new_destination:
        new_destination.destination = data.get("destination",new_destination.destination)
        new_destination.country = data.get("country",new_destination.country)
        new_destination.rating = data.get("rating",new_destination.rating)

        db.session.commit()
        return jsonify(new_destination.to_dict())

    else:
        return jsonify({"error": "Destination not found!"}), 404


# DELETE
@app.route("/destinations/<int:destination_id>", methods = ["DELETE"])
def del_destination(destination_id):
    destination2 = db.session.get(destination_id, Destination)

    if destination2:
        db.session.delete(destination2)
        db.session.commit()

        return jsonify({"Message" : "Destination was deleted"})

    else:
        return jsonify({"error": "Destination not found!"}), 404


# ADDING THE AI LAYER
@app.route("/destinations/<int:destination_id>/features", methods =["POST"])
def features(destination_id):
    destination3 = db.session.get(destination_id, Destination)
    if not destination3:
        return jsonify({"Error" : "Destination not found"}), 404
    # connecting to ollama's api
    client = Client(
        host="https://ollama.com",
        headers= {"Authorization" : "Bearer " + os.getenv("OLLAMA_API_KEY")}
    )

    response = client.chat(
        model="qwen3.5:397b-cloud",
        messages= [{ "role" : "user",
                    "content" : f"Give me features about {destination3.destination}, be precise and specific."
          }]
    )

    # extracting the text response
    features1 = response['message']['content']

    return jsonify({
        "Destination" : destination3.destination,
        "country" : destination3.country,
        "Features" : features1
     })














if __name__ == "__main__":
    app.run(debug=True)