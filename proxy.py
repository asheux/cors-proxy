import time
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import or_

from corsproxy.veribot import VeriBot3000
from corsproxy.s3_client import S3Client
from corsproxy.models import User, Vote, Block, db
from blockchain.hashing import Blockchain
from create_app import app

migrate = Migrate(app, db)


@app.route('/')
@app.route('/index')
def index():
    return """
        <div style='text-align: center; margin-top: 3em;'>
            <h1>
                Hello friend! Welcome! This is a portal to a free world.
            </h1>
        </div>
    """

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

    if len(name) > 50:
        return jsonify({'error': {'name': 'Name too long.'}}), 400

    description = data.get('description')
    link = data.get('link')
    if not description or len(description.split(" ")) < 21:
        if not description:
            counter = 0
        else:
            counter = len(description.split(' '))

        message = f"Come on! I think you can do better than {counter} words, don't you think?"
        errormessage = {'description': message}
        return jsonify({'error': errormessage}), 400

    user = User.query.filter_by(name=name).first()
    latest_block = Block.query.order_by(Block.index.desc()).first()
    if user is not None:
        latest_block.user = user
        user.grokcoins += 1
        db.session.commit()
        message = "In any perfect world, one vote is allowed. But hey, you got a GovCoin!"
        errormessage = {'name': message}
        return jsonify({'error': errormessage}), 400

    new_user = User(name=name, thought=description, link=link)
    latest_block.user = new_user
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
    search_query = request.args.get('search')
    if search_query:
        userthoughts = User.query.filter(or_(
            User.name.ilike(f'%{search_query}'),
            User.thought.ilike(f'%{search_query}')
        )).all()
    else:
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
        return jsonify({'error': 'File is not provided.'}), 400

    try:
        v = VeriBot3000()
        message, status = v.is_valid(file)
        return jsonify(message), status
    except Exception as error:
        return jsonify({'error': 'Failed to upload image. Try again.'}), 400

@app.route('/detectrash', methods=['POST'])
def detectrash():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'File is not provided'}), 400

    try:
        v = VeriBot3000()
        is_trash_detected = v.detect_trash(file)
        if not is_trash_detected:
            return jsonify({
                'error': 'No trash detected in the image. GovTrash AI is not perfect. Try again!'
            }), 400
        return jsonify({'data': {'success': 'Trash detected in the image.'}}), 200
    except Exception as error:
        return jsonify({'error': 'Failed to upload image. Try again.'}), 400


@app.route('/blockchain', methods=['POST'])
def blockchain():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'File is not provided'}), 400

    blob = request.files.get("blob")
    project_name = request.form.get("project_name")
    bc = Blockchain()
    already_exists, image_hash = bc.process_image(file)
    if already_exists:
        return jsonify({'error': 'Image already exists. Try a different image taken by you.'}), 400

    # Store image to S3
    block = Block.query.order_by(Block.index.desc()).first()
    s3 = S3Client()
    file_name = f"blockchain_uploaded_file_{time.time()}_{file.filename}".strip()
    try:
        resource_url = s3.upload_file_to_s3(file_name, blob)
        block.image_link = resource_url
        block.project_name = project_name
        db.session.commit()
        return jsonify({'data': {"status": "successfully"}}), 200
    except Exception as err:
        return jsonify({'error': 'An error occurred when upload. Please try again.'})


@app.route('/blocks', methods=["GET"])
def blocks():
    project_name = request.args.get('project_name')
    imageblocks = Block.query.filter_by(project_name=project_name).all()
    all_blocks = [ibk.to_dict() for ibk in imageblocks]
    return jsonify({'data': all_blocks})
