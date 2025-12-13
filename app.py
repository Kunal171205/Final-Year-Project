from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import os

app = Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test")
def test():
    return "Flask app is running! ✅"

if __name__ == "__main__":
    app.run(debug=True)