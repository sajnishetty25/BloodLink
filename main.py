from flask import Flask
from flask_session import Session
from server import server 
import login   # This is your login.py file (which creates a Dash app with routes_pathname_prefix '/login/')
import dashboard
import app 
import recipients  
# This is your app.py file (which creates a Dash app with routes_pathname_prefix '/dashboard/')

if __name__ == '__main__':
    server.run(debug=True, port=8051)