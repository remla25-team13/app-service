from flask import Flask, request, jsonify, Response
from flasgger import Swagger
from flask_cors import CORS
import requests
import os
import time
from lib_version.version_util import VersionUtil

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL")
failed_predictions = 0
predictions = 0
last_req_time = 0

correct_pred = 0
wrong_pred = 0

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
    global predictions, last_req_time, failed_predictions

    input_data = request.get_json()
    try:
        start = time.time()
        response = requests.post(f"{MODEL_SERVICE_URL}/predict", json=input_data)
        end = time.time()
        
        predictions += 1
        last_req_time = end - start

        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        failed_predictions += 1
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
    """
    global correct_pred, wrong_pred

    body = request.get_json()
    predicted = body['predicted']
    corrected = body['corrected']
    review = body['review']

    if predicted == corrected:
      correct_pred += 1
    else:
      wrong_pred += 1

    # TODO save (review, correct) pair 

    return "Thank you for submitting"
    

@app.route('/metrics', methods=['GET'])
def metrics():
  global predictions, last_req_time, failed_predictions, correct_pred, wrong_pred

  # Predictions
  # This can be used as a template the add more metrics
  m = "# HELP predictions This is a counter keeping track of the total amount of predictions made.\n"
  m+= "# TYPE predictions counter\n" # counter | gauge
  m+= f"predictions {predictions} \n"

  m+= "# HELP failed_predictions This is a counter keeping track of the total amount of failed predictions attempts caused by techincal errors.\n"
  m+= "# TYPE failed_predictions counter\n"
  m+= f"failed_predictions {failed_predictions}\n"

  m+= "# HELP correct_pred This is a counter keeping track of the total amount of correct predictions.\n"
  m+= "# TYPE correct_pred counter\n"
  m+= f"correct_pred {correct_pred}\n"

  m+= "# HELP wrong_pred This is a counter keeping track of the total amount of wrong predictions.\n"
  m+= "# TYPE wrong_pred counter\n"
  m+= f"wrong_pred {wrong_pred}\n"

  # TODO decide how exactly we want to track this (i.e. last req time or avg req time)
  m+= "# HELP last_req_time This is a gauge measuring the amount of time it took the last request to complete.\n"
  m+= "# TYPE last_req_time gauge\n"
  m+= f"last_req_time {last_req_time}\n"
  
  m+= "# HELP accuracy This is a gauge measuring the accuracy of the model.\n"
  m+= "# TYPE accuracy gauge\n"

  total = max(correct_pred + wrong_pred, 1)
  m+= f"accuracy {correct_pred / total}\n"

  return Response(m, mimetype="text/plain")  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)