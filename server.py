from flask import Flask
from flask_session import Session

server = Flask(__name__)
server.secret_key = "your_secret_key"
server.config["SESSION_TYPE"] = "filesystem"
Session(server)
