from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from create_app import app


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    thought = db.Column(db.Text())
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    grokcoins = db.Column(db.Integer, default=1)
    link = db.Column(db.String(256), nullable=True)

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
            'link': self.link,
        }


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', backref=db.backref('votes', lazy=True))


class Block(db.Model):
    __tablename__ = 'blockchain'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    index = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_hash = db.Column(db.String(256), nullable=False, unique=True)
    block_hash = db.Column(db.String(256), nullable=False)
    previous_hash = db.Column(db.String(256), nullable=False)
    image_link = db.Column(db.String(256), nullable=True)
    project_name = db.Column(db.String(100), unique=True, nullable=False)
    user = db.relationship('User', backref=db.backref('blocks', lazy=True))

    def __repr__(self):
        return f'<Block {self.index}>'

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "image_link": self.image_link,
            "created_by": self.user.name if self.user else None,
        }
