import time
import requests
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from veribot import VeriBot3000
from s3_client import S3Client

# Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/tccup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    thought = db.Column(db.Text())
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    grokcoins = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Thought {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'name': self.name,
            'thought': self.thought,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'grokcoins': self.grokcoins,
        }


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', backref=db.backref('votes', lazy=True))


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

    if len(name) > 100:
        return jsonify({'error': {'name': 'Name too long.'}}), 400

    description = data.get('description')
    if not description or len(description.split(" ")) < 21:
        if not description:
            counter = 0
        else:
            counter = len(description.split(' '))

        message = f"Come on! I think you can do better than {counter} words, don't you think?"
        errormessage = {'description': message}
        return jsonify({'error': errormessage}), 400

    user = User.query.filter_by(name=name).first()
    if user is not None:
        user.grokcoins += 1
        db.session.commit()
        message = "In any perfect world, one vote is allowed. But hey, you got a GovCoin!"
        errormessage = {'name': message}
        return jsonify({'error': errormessage}), 400

    new_user = User(name=name, thought=description)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'data': {
            'message': 'Thought created successfully!',
            'user': {
                'name': name,
                'thought': description
            }
        }
    }), 201


@app.route('/thoughts', methods=['GET'])
def thoughts():
    userthoughts = User.query.order_by(User.created_at.desc()).all()
    all_thoughts = [t.to_dict() for t in userthoughts]
    return jsonify({'data': all_thoughts})


@app.route('/thoughts/<int:user_id>/upvote', methods=['POST'])
def upvote(user_id):
    vote = request.json.get('vote')
    if not vote or vote >= 1:
        vote = 1
    user = User.query.get_or_404(user_id)
    new_vote = Vote(user_id=user_id, vote_type='upvote')
    db.session.add(new_vote)
    user.upvotes += vote

    db.session.commit()
    return jsonify({'data': {'message': 'Agreed successfully'}}), 200

@app.route('/thoughts/<int:user_id>/downvote', methods=['POST'])
def downvote(user_id):
    vote = request.json.get('vote')
    if not vote or vote >= 1:
        vote = 1
    user = User.query.get_or_404(user_id)
    new_vote = Vote(user_id=user_id, vote_type='downvote')
    db.session.add(new_vote)
    user.downvotes += vote

    db.session.commit()
    return jsonify({'data': {'message': 'Disagreed successfully'}}), 200

@app.route('/veribot', methods=['POST'])
def veribot():
    file = request.files.get('file')
    if not file:
        return {'error': 'File is not provided'}

    try:
        file_name = f"user_uploaded_file_{time.time()}-{file.filename}".strip()
        s3 = S3Client()
        s3.upload_temp_file_to_s3(file_name, file)
        v = VeriBot3000()
        message, status = v.is_valid(file, 'trash_detection_model.pt')
        return message, status
    except Exception as error:
        return {'error': 'File to upload image'}, 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
