import requests

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from veribot import VeriBot3000

# Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/tccup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)

class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text())

    def __repr__(self):
        return f'<Thought {self.name}>'

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

@app.route('/thought', methods=['POST'])
def thought():
    data = request.get_json()
    if not data:
        return jsonify({{'error': 'Invalid input'}}), 400

    name = data.get('name')
    if not name:
        return jsonify({'error': {'name': 'Name is required to submit.'}}), 400

    description = data.get('description')
    if not description or len(description.split(" ")) < 50:
        if not description:
            counter = 0
        else:
            counter = len(description.split(' '))

        return jsonify({
            'error': {
                "description": f"Come on! I think you can do more than {counter} words, don't you think"
            }
        }), 400

    new_thought = Thought(name=name, description=description)
    db.session.add(new_thought)
    db.session.commit()

    return jsonify({'message': 'User created successfully!'}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
