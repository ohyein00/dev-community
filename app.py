from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient('54.218.128.24', 27017, username="test", password="test")
db = client.dbtest


@app.route('/')
def main():
    return render_template("index.html")


@app.route("/list", methods=["GET"])
def web_mars_get():
    order_list = list(db.mars.find({},{'_id':False}))
    print(order_list)
    return jsonify({'data':order_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

