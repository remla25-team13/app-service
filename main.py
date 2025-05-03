from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Hello, World!", 200

@app.route("/create", methods=["POST"])
def create():
    return "Create operation", 200

@app.route("/read", methods=["GET"])
def read():
    return "Read operation", 200

@app.route("/update", methods=["PUT"])
def update():
    return "Update operation", 200

@app.route("/delete", methods=["DELETE"])
def delete():
    return "Delete operation", 200