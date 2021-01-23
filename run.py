from dash_app.app import app
from dash_app.settings import SERVER_SETTINGS

server = app.server

def main():
    app.run_server(
        host=SERVER_SETTINGS["host"],
        port=SERVER_SETTINGS["port"],
        debug=SERVER_SETTINGS["debug"],
    )


if __name__ == "__main__":
    main()
