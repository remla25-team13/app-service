from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

swagger = Swagger(app)

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL")

@app.route("/", methods=["GET"])
def home():
    """
    Home endpoint returning a greeting.
    ---
    responses:
      200:
        description: A greeting message
    """
    return "Hello, World! From app-service."

@app.route("/create", methods=["POST"])
def create():
    """
    Create endpoint to perform a create operation.
    ---
    responses:
      200:
        description: Create operation successful
    """
    return "Create operation"

@app.route("/read", methods=["GET"])
def read():
    """
    Read endpoint to perform a read operation.
    ---
    responses:
      200:
        description: Read operation successful
    """
    return "Read operation"

@app.route("/update", methods=["PUT"])
def update():
    """
    Update endpoint to perform an update operation.
    ---
    responses:
      200:
        description: Update operation successful
    """
    return "Update operation"

@app.route("/delete", methods=["DELETE"])
def delete():
    """
    Delete endpoint to perform a delete operation.
    ---
    responses:
      200:
        description: Delete operation successful
    """
    return "Delete operation"

@app.route("/version", methods=["GET"])
def version():
    """
    Version endpoint that returns the application version.
    ---
    responses:
      200:
        description: Application version in JSON format
    """
    return {"version": "0.0.3"}

@app.route("/predict", methods=["POST"])
def predict():
    """
    Forward a review to the model-service for sentiment prediction.
    ---
    consumes:
      - application/json
    parameters:
      - name: input_data
        in: body
        required: true
        schema:
          type: object
          required: [review]
          properties:
            review:
              type: string
              example: This is a great restaurant!
    responses:
      200:
        description: Sentiment prediction from model-service
    """
    input_data = request.get_json()
    try:
        response = requests.post(f"{MODEL_SERVICE_URL}/predict", json=input_data)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)