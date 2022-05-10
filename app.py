from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta

import certifi
import hashlib
import jwt
import datetime


ca = certifi.where()
client = MongoClient('3.34.47.86', 27017, username="test", password="test")
db = client.dbsparta

app = Flask(__name__)

SECRET_KEY = 'SPARTA'

@app.route('/')
def main():
    myname = "Devom"
    return render_template("index.html", name=myname)


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    name_receive = request.form['name_give']
    nickname_receive = request.form['nickname_give']

    doc = {
        "username": username_receive,
        "password": password_hash,
        "name": name_receive,
        "nickname": nickname_receive,
        "img": "profile_pics/profile_placeholer.png",
        "text": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup_username', methods=['POST'])
def check_dup_username():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/check_dup_nickname', methods=['POST'])
def check_dup_nickname():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)