import os
import random
import time

import requests
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from lib_version.version_util import VersionUtil
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
CORS(app)
swagger = Swagger(app)

MODEL_SERVICE_URL_A = os.getenv("MODEL_SERVICE_URL_A")
MODEL_SERVICE_URL_B = os.getenv("MODEL_SERVICE_URL_B")
A_B_RATE = float(os.getenv("A_B_RATE", "0.5"))

# Prometheus metrics using prometheus_flask_exporter
prediction_counter = metrics.counter(
    "predictions",
    "Total predictions made",
    labels={"type": lambda: getattr(request, "model_type", "unknown")},
)
failed_prediction_counter = metrics.counter(
    "failed_predictions",
    "Total failed prediction attempts",
    labels={"type": lambda: getattr(request, "model_type", "unknown")},
)
correct_pred_counter = metrics.counter(
    "correct_pred",
    "Total correct predictions",
    labels={"type": lambda: getattr(request, "model_type", "unknown")},
)
wrong_pred_counter = metrics.counter(
    "wrong_pred",
    "Total wrong predictions",
    labels={"type": lambda: getattr(request, "model_type", "unknown")},
)
last_req_time_gauge = metrics.gauge(
    "last_req_time",
    "Time taken for last request",
    labels={"type": lambda: getattr(request, "model_type", "unknown")},
)
accuracy_gauge = metrics.gauge(
    "accuracy",
    "Accuracy of the model",
    labels={"type": lambda: getattr(request, "model_type", "unknown")},
)

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
    input_data = request.get_json()
    try:
        start = time.time()
        url, model_type = get_model_service_url()
        request.model_type = model_type  # set for metrics
        response = requests.post(f"{url}/predict", json=input_data)
        end = time.time()

        prediction_counter.inc()
        last_req_time_gauge.set(end - start)

        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        _, model_type = get_model_service_url()
        request.model_type = model_type
        failed_prediction_counter.inc()
        return jsonify({"error": str(e)}), 500


@app.route("/submit", methods=["POST"])
def submit():
    body = request.get_json()
    predicted = body["predicted"]
    corrected = body["corrected"]
    model_type = body["model_type"].lower()
    request.model_type = model_type
    review = body["review"]

    if predicted == corrected:
        correct_pred_counter.inc()
        correct_wrong_counts[model_type]["correct"] += 1
    else:
        wrong_pred_counter.inc()
        correct_wrong_counts[model_type]["wrong"] += 1

    total = (
        correct_wrong_counts[model_type]["correct"]
        + correct_wrong_counts[model_type]["wrong"]
    )
    if total > 0:
        accuracy = correct_wrong_counts[model_type]["correct"] / total
        accuracy_gauge.set(accuracy)

    return "Thank you for submitting"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
