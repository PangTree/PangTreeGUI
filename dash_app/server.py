from flask import Flask, session
from flask_session import Session
from dash import Dash

server = Flask('PangTree')
server.config.from_object(__name__)
server.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
 
app = Dash(
    __name__,
    external_stylesheets=['https://use.fontawesome.com/releases/v5.8.1/css/all.css'],
    server=server,
    title='PangTreeGUI',
    update_title=None
)
app.title = 'PangTreeGUI'
app.config.suppress_callback_exceptions = True
