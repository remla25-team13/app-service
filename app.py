import os
import random
import time

import requests
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from lib_version.version_util import VersionUtil
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge

app = Flask(__name__)
metrics = PrometheusMetrics(app)
CORS(app)
swagger = Swagger(app)

MODEL_SERVICE_URL_A = os.getenv("MODEL_SERVICE_URL_A")
MODEL_SERVICE_URL_B = os.getenv("MODEL_SERVICE_URL_B")
A_B_RATE = float(os.getenv("A_B_RATE", "0.5"))

# Prometheus metrics using prometheus_flask_exporter
prediction_counter = Counter("predictions_total", "Total predictions made", ["model_type"])
failed_prediction_counter = Counter(
    "failed_predictions_total", "Total failed prediction attempts", ["model_type"]
)
correct_pred_counter = Counter(
    "correct_pred_total", "Total correct predictions", ["model_type"]
)
wrong_pred_counter = Counter("wrong_pred_total", "Total wrong predictions", ["model_type"])
last_req_time_gauge = Gauge(
    "last_req_time_seconds", "Time taken for last request", ["model_type"]
)
accuracy_gauge = Gauge("accuracy", "Accuracy of the model", ["model_type"])

# Track correct/wrong for accuracy calculation
correct_wrong_counts = {
    "gauss": {"correct": 0, "wrong": 0},
    "multi": {"correct": 0, "wrong": 0},
}


def get_model_service_url():
    if random.random() > A_B_RATE:
        return MODEL_SERVICE_URL_A, "gauss"
    return MODEL_SERVICE_URL_B, "multi"


@app.route("/", methods=["GET"])
def home():
    """
    Home endpoint returning a greeting.
    ---
    responses:
      200:
        description: A greeting message
    """
    print(app.url_map)
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


@app.route("/version/app-service", methods=["GET"])
def app_service_version():
    """
    Version endpoint that returns the application version.
    ---
    responses:
      200:
        description: Application version in JSON format
    """
    return {"version": "0.0.3"}


@app.route("/version/lib-version", methods=["GET"])
def lib_version():
    """
    Version endpoint that returns the lib-version library version.
    ---
    responses:
      200:
        description: Library version in JSON format
        examples:
          application/json: { "version": "1.0.0" }
    """
    return {"version": VersionUtil.get_version()}


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
        start = time.time()
        url, model_type = get_model_service_url()
        request.model_type = model_type  # set for metrics
        response = requests.post(f"{url}/predict", json=input_data)
        end = time.time()

        prediction_counter.labels(model_type=model_type).inc()
        last_req_time_gauge.labels(model_type=model_type).set(end - start)

        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        _, model_type = get_model_service_url()
        request.model_type = model_type
        failed_prediction_counter.labels(model_type=model_type).inc()
        return jsonify({"error": str(e)}), 500


@app.route("/submit", methods=["POST"])
def submit():
    """
    Submit review to dataset.
    ---
    consumes:
      - application/json
    parameters:
      - name: input_data
        in: body
        required: true
        schema:
          type: object
          required: [predicted, corrected, review]
          properties:
            predicted:
              type: boolean
              example: True
            corrected:
              type: boolean
              example: False
            review:
              type: string
              example: This is a great restaurant!
            model_type:
              type: string
              example: Gauss or Multi
    """
    body = request.get_json()
    predicted = body["predicted"]
    corrected = body["corrected"]
    model_type = body["model_type"].lower()
    request.model_type = model_type
    review = body["review"]

    if predicted == corrected:
        correct_pred_counter.labels(model_type=model_type).inc()
        correct_wrong_counts[model_type]["correct"] += 1
    else:
        wrong_pred_counter.labels(model_type=model_type).inc()
        correct_wrong_counts[model_type]["wrong"] += 1

    total = (
        correct_wrong_counts[model_type]["correct"]
        + correct_wrong_counts[model_type]["wrong"]
    )
    if total > 0:
        accuracy = correct_wrong_counts[model_type]["correct"] / total
        accuracy_gauge.labels(model_type=model_type).set(accuracy)

    return "Thank you for submitting"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
