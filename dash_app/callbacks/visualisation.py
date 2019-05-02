from dash.exceptions import PreventUpdate

from ..server import app
from dash.dependencies import Input, Output
from ..layout.layout_ids import *
from ..components import tools


@app.callback(
    Output(id_pangenome_hidden, 'children'),
    [Input(id_pangenome_upload, 'contents')])
def load_visualisation(pangenome_content: str) -> str:
    if not pangenome_content:
        raise PreventUpdate()
    if pangenome_content.startswith("data:application/json;base64"):
        return tools.decode_content(pangenome_content)
    return pangenome_content







