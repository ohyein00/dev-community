import codecs
import re
import gridfs

from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://qwerty35043:qwerty35043@cluster0.wnazh.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.db
fs = gridfs.GridFS(db)

def get_img_file(img_id):
    img_binary = fs.get(img_id)
    base64_img = codecs.encode(img_binary.read(), 'base64')
    decoded_img = base64_img.decode('utf-8')
    return decoded_img

@app.route('/')
def main():
    myname = "Devom"
    return render_template("index.html", name=myname)

@app.route('/write')
def write():
    return render_template("write.html")

@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        text_receive = request.form['text']
        date_receive = request.form['date']

        pattern = '#([0-9a-zA-Z가-힣]*)'
        find_hash = re.compile(pattern)
        hash_tags = find_hash.findall(text_receive)

        img_ids = []
        if request.files is not None:
            for file in request.files:
                img_id = fs.put(request.files[file])
                img_ids.append(img_id)

        db.tmp.insert_one({
            'date': date_receive,
            'text': text_receive,
            'hash_tags': hash_tags,
            'img_ids': img_ids
        })

        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/read', methods=['GET'])
def read():
    return render_template("read.html")

@app.route('/read_result', methods=['GET'])
def read_result():
    receive_id = int(request.args['id'])
    content = db.tmp.find_one({'id': receive_id})
    img_ids = content['img_ids']

    result = []

    if len(img_ids) > 0:
        for img_id in img_ids:
            result.append(get_img_file(img_id))

    print(result)
    return jsonify({'result': 'success', 'files': result})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)