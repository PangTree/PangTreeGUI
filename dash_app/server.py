from flask import Flask, session
from flask_session import Session
from dash import Dash

server = Flask('pangenome')
SESSION_TYPE = 'filesystem'
server.config.from_object(__name__)
server.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app = Dash(__name__, server=server)

