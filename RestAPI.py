import re
import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, make_response
from flask_swagger_ui import get_swaggerui_blueprint

# Init app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

#Database
db = sqlite3.connect('data.db', check_same_thread=False)
db.row_factory = sqlite3.Row
mycursor = db.cursor()
db.execute('''CREATE TABLE IF NOT EXIST data(id INTEGER PRIMARY KEY AUTOINCREMENT, old_text varchar(255), new_text varchar(255));''')

# flask swagger configs
SWAGGER_URL = '/swagger'
API_URL = 'static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Text cleansing"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


# Homepage
@app.route('/', methods=['GET'])
def get():
    return "Welcome guys"


# Tweet
@app.route("/tweet", methods=["GET", "POST"])
def tweet():
    if request.method == "POST":
        text = str(request.form["text"])
        text_clean = re.sub(r'[^0-9a-zA-Z]+', ' ', '\n',' ', 'rt',' ', 'user',' ', '((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ', '  +',' ', text)
        query_text = "insert into tweet (old_text, new_text) values (?,?)"
        val = (text, text_clean)
        mycursor.execute(query_text, val)
        db.commit()
        print(text)
        print(text_clean)
        return "Success input data"

    elif request.method == "GET":
        query_text = "select * from tweet"
        select_tweet = mycursor.execute(query_text)
        tweet = [
            dict(id=row[0], old_text=row[1], new_text=row[2])
            for row in select_tweet.fetchall()
        ]
        return jsonify(tweet)


@app.route("/tweet/<string:id>", methods=["GET", "PUT", "DELETE"])
def id(id):
    if request.method == "GET":

        query_text = "select * from tweet where id = ?"
        val = str(id)
        select_tweet = mycursor.execute(query_text, [val])
        tweet = [
            dict(id=row[0], old_text=row[1], new_text=row[2])
            for row in select_tweet.fetchall()
        ]
        print(tweet)
        return jsonify(tweet)

    elif request.method == "DELETE":

        query_text = "delete from tweet where id = ?"
        val = id
        mycursor.execute(query_text, [val])
        db.commit()
        return "Success delete data"

    elif request.method == "PUT":

        text = str(request.form["text"])
        text_clean =  re.sub(r'[^0-9a-zA-Z]+', ' ', '\n',' ', 'rt',' ', 'user',' ', '((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ', '  +',' ', text)
        query_text = "update tweet set old_text = ?, new_text = ?, where id = ?"
        val = (text, text_clean,id)
        mycursor.execute(query_text, val)
        db.commit()

        return "Success update data"

# Upload CSV Files
@app.route("/tweet/csv", methods=["POST"])
def tweet_csv():
    if request.method == 'POST':
        file = request.files['file']

        try:
            data = pd.read_csv(file, encoding='iso-8859-1')
        except:
            data = pd.read_csv(file, encoding='utf-8')
        (data)
        return "Upload Success"


# Error handling
@app.errorhandler(400)
def handle_400_error(_error):
    "Return a http 400 error to client"
    return make_response(jsonify({'error': 'Misunderstood'}), 400)

@app.errorhandler(401)
def handle_401_error(_error):
    "Return a http 401 error to client"
    return make_response(jsonify({'error': 'Unauthorised'}), 401)

@app.errorhandler(404)
def handle_404_error(_error):
    "Return a http 404 error to client"
    return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(500)
def handle_500_error(_error):
    "Return a http 500 error to client"
    return make_response(jsonify({'error': 'Server Error'}), 500)


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
# Default IP 127.0.0.1 Port 5000
