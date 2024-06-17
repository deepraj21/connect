# CONNECT : Real-Time Chat Application with Blockchain Integration

This project is a chat application with a unique feature: messages are stored on a blockchain to ensure data integrity and security. The application supports real-time communication, message replies, and user avatars via Gravatar.

## Features

- **Blockchain Integration**: Messages are stored on a blockchain to ensure data integrity.
- **Real-time Chat**: Powered by Socket.IO, enabling instant message exchange.
- **Reply Functionality**: Users can reply to specific messages in the chat.
- **Gravatar Integration**: User avatars are generated using Gravatar based on their email addresses.
- **User Authentication**: Users can sign up and log in to the chat application.

## Prerequisites

- Python 3.x
- Flask
- Flask-SocketIO
- PyMongo
- Requests
- Validate-Email-Address
- Gunicorn
- Dotenv

## Installation guide for Contribution

1. **Clone the repository**:
    ```bash
    git clone https://github.com/deepraj21/connect.git
    cd connect
    ```

2. **Create venv and Install the dependencies**:
    ```bash
    python -m venv venv
    ./venv/Scripts/activate
    pip install -r requirements.txt
    ```

3. **Set up environment variables**:
    - Create a `.env` file in the root directory.
    - Add the following environment variables:
      ```bash
      SECRET_KEY=your_secret_key
      MONGO_CONNECTION_STRING=mongodb_uri
      ```

4. **Run the application**:
    ```bash
    python app.py or flask run
    ```

## Project Structure

```arduino
connect/
├── blockchain/
│   └── __init__.py
│   └── blockchain.py
├── templates/
│   ├── index.html
│   └── chat.html
├── static/
│   └── css/
│       └── styles.css
├── .env
├── app.py
├── requirements.txt
└── README.md
```

## Webapp Preview

<img src="webapp preview/img1.png">
<img src="webapp preview/img2.png">
<img src="webapp preview/img3.png">

## `app.py` Explained

### Flask Application

- **Initialization**:
  - Set up the Flask application and configure it with a secret key.
  - Initialize Socket.IO for real-time communication.
  - Connect to MongoDB for storing user and message data.
  - Initialize the blockchain.

- **Helper Functions**:
  - `get_gravatar_url(email)`: Generates a Gravatar URL based on the user's email.

### Socket.IO Events

- **`handle_message`**:
  - Handles incoming messages.
  - Validates user session.
  - Saves the message to MongoDB.
  - Adds the message to the latest block in the blockchain.
  - Broadcasts the message to all connected clients.

### Routes

- **`/signup`**:
  - Handles user registration.
  - Validates email and checks if the user already exists.
  - Hashes the password and stores the user data in MongoDB.

- **`/login`**:
  - Handles user login.
  - Validates user credentials.
  - Creates a session for the user.

- **`/`**:
  - Renders the chat page if the user is logged in.
  - If not logged in, redirects to the login/signup page.

- **`/mine_block`**:
  - Mines a new block and adds it to the blockchain.
  - Returns the details of the mined block.

- **`/get_chain`**:
  - Returns the entire blockchain.

- **`/valid`**:
  - Checks if the blockchain is valid.

- **`/logout`**:
  - Logs out the user by clearing the session.

## Blockchain Class

### `blockchain/blockchain.py`

- **Initialization**:
  - Initializes the blockchain with the genesis block.

- **Methods**:
  - `create_block(proof, previous_hash)`: Creates a new block and adds it to the blockchain.
  - `print_previous_block()`: Returns the last block in the blockchain.
  - `proof_of_work(previous_proof)`: Generates proof of work for mining a new block.
  - `hash(block)`: Generates a SHA-256 hash for a block.
  - `chain_valid(chain)`: Validates the blockchain.

## How It Works

1. **User Registration/Login**:
   - Users can sign up with a username, email, and password.
   - Upon login, a session is created, and the user can access the chat page.

2. **Real-time Chat**:
   - Users can send messages in real-time.
   - Each message is broadcast to all connected clients and stored in the blockchain.

3. **Message Reply**:
   - Users can reply to specific messages.
   - The reply includes the original message and the username of the original sender.

4. **Blockchain Storage**:
   - Messages are stored in the latest block of the blockchain.
   - A new block is mined periodically to secure the data.

5. **Gravatar Integration**:
   - User avatars are generated using Gravatar based on their email addresses.


## Conclusion

This chat application leverages blockchain technology to ensure data integrity and security while providing real-time communication and user-friendly features like message replies and Gravatar integration.