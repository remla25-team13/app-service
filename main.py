from flask import Flask, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/", methods=["GET"])
def home():
    """
    Home endpoint returning a greeting.
    ---
    responses:
      200:
        description: A greeting message
    """
    return "Hello, World!"

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)