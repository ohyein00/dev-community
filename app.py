from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for


client = MongoClient('3.34.47.86', 27017, username="test", password="test")
db = client.devom

app = Flask(__name__)


@app.route('/')
def main():
    myname = "Devom"
    return render_template("index.html", name=myname)

@app.route('/like_list')
def like_list():
    return render_template("like_list.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/post_content')
def profile():
    return render_template("post_content.html")

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)