from dash_app.app import app

server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, port=8052, dev_tools_ui=True)
