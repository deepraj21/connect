from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response, flash
import requests
from flask_socketio import SocketIO, emit
import pymongo
import hashlib
import datetime
from validate_email import validate_email
from bson import ObjectId
import uuid
import os
from dotenv import load_dotenv
import gunicorn
from blockchain.blockchain import Blockchain

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app)

# MongoDB connection
client = pymongo.MongoClient('mongodb+srv://deepraj21bera:FrLjA6dAdYWMP51U@cluster0.sfykkgk.mongodb.net/')
db = client["chat_app"]
users_collection = db["users"]
messages_collection = db["messages"]

blockchain = Blockchain()

########################################## FUNCTIONS ##########################################

def get_gravatar_url(email):
    email = email.strip().lower()
    email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon"
    return gravatar_url


@socketio.on('message')
def handle_message(message):
    user_id = session.get('user_id')
    if user_id:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            username = user['username']
            email = user['email']
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message_text = message['message']
            message_hash = hashlib.sha256(message_text.encode()).hexdigest()
            reply_to = message.get('reply_to')
            reply_to_username = message.get('reply_to_username')
            
            # Find the original message if replying
            if reply_to:
                original_message = messages_collection.find_one({'_id': ObjectId(reply_to)})
                if original_message:
                    reply_to_username = original_message['username']
                    message['reply_to_username'] = reply_to_username
                    message['reply_to_message'] = original_message['message']
                else:
                    reply_to = None  # Reset reply_to if original message not found
            
            new_message = {
                'username': username,
                'email': email,
                'message': message_text,
                'timestamp': timestamp,
                'hash': message_hash,
                'reply_to': reply_to,
                'reply_to_username': reply_to_username,
                'reply_to_message': message.get('reply_to_message') if 'reply_to_message' in message else None
            }

            messages_collection.insert_one(new_message)
            blockchain.chain[-1]['messages'].append(new_message)
            new_message['_id'] = str(new_message['_id'])
            new_message['gravatar_url'] = get_gravatar_url(email)

            emit('message', new_message, broadcast=True)
    else:
        emit('error', {'message': 'User not logged in'}, broadcast=False)
        
########################################## ROUTES ##########################################

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if users_collection.find_one({'email': email}):
        flash('User already exists')
        return redirect(url_for('home'))

    is_valid_email = validate_email(
        email_address=email,
        check_format=True,
        check_blacklist=True,
        check_dns=True,
        check_smtp=True
    )
    
    if not is_valid_email:
        flash('Invalid email address')
        return redirect(url_for('home'))

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user_data = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'verified': True
    }
    users_collection.insert_one(user_data)

    flash('Registration successful. You can now log in.')
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = users_collection.find_one({'username': username})

    if not user:
        flash('User not found')
        return redirect(url_for('home'))

    if not user['verified']:
        flash('Email not verified')
        return redirect(url_for('home'))

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user['password'] != hashed_password:
        flash('Invalid password')
        return redirect(url_for('home'))

    session_id = str(uuid.uuid4())
    session['user_id'] = str(user['_id'])
    session['session_id'] = session_id

    resp = make_response(redirect(url_for('chat')))
    resp.set_cookie('session_id', session_id)

    return resp

@app.route('/')
def chat():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('index.html')

    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return "User not found", 404
    
    username = user['username']
    email = user['email']
    gravatar_url = get_gravatar_url(email)
    chat_history = list(messages_collection.find())
    for msg in chat_history:
        msg['gravatar_url'] = get_gravatar_url(msg['email'])
        if msg['reply_to']:
            reply_message = messages_collection.find_one({'_id': ObjectId(msg['reply_to'])})
            msg['reply_to_username'] = reply_message['username']
            msg['reply_to_message'] = reply_message['message']
    return render_template('chat.html', username=username, gravatar_url=gravatar_url, chat_history=chat_history)

########################################## ROUTES for HASHING ##########################################

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'A block is MINED',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def display_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/valid', methods=['GET'])
def valid():
    is_valid = blockchain.chain_valid(blockchain.chain)

    if is_valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

# if __name__ == '__main__':
#     socketio.run(app, debug=True,use_reloader=True)
