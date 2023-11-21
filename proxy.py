import requests

from flask import Flask, request
from flask_cors import CORS

from settings import *


app = Flask(__name__)
CORS(app)

@app.route('/crawl', methods=['GET'])
def crawl():
    url = request.args.get("url") # get url to crawl
    res = requests.get(url)
    if res.status_code == 200:
        body = res.text
    else:
        body = res.reason
    return body

if __name__ == "__main__":
    app.run(debug=APP_DEBUG)
