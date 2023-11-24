import requests

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/crawl', methods=['GET'])
def crawl():
    message = ""
    try:
        url = request.args.get("url") # get url to crawl
        res = requests.get(url)

    except Exception as error:
        res = None
        message = f"Error making request: {error}"

    if res is None:
        return message

    if res.status_code == 200:
        body = res.text
    else:
        body = res.reason
    return body

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
