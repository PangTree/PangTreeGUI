import dash

from dash_app.components.layout import generate_layout
from dash_app.settings import APP_SETTINGS

app = dash.Dash(
    __name__,
    external_stylesheets=APP_SETTINGS["stylesheets"],
    suppress_callback_exceptions=True,
    title=APP_SETTINGS["title"],
    update_title=None
)

app.layout = generate_layout()

