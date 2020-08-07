import pandas as pd
from typing import List

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.components import tools, poagraph
from dash_app.layout.pages import get_task_description_layout
from dash_app.server import app


@app.callback(
    Output("pangenome_hidden", 'children'),
    [Input("pangenome_upload", 'contents')])
def load_visualisation(pangenome_content):
    if not pangenome_content:
        raise PreventUpdate()
    if pangenome_content.startswith("data:application/json;base64"):
        return tools.decode_content(pangenome_content)
    return pangenome_content


@app.callback(
    Output("pangviz_result_collapse", 'is_open'),
    [Input("pangenome_upload", 'contents')])
def show_visualisation(pangenome_content):
    if pangenome_content and pangenome_content.startswith("data:application/json;base64"):
        return True
    return False


@app.callback(Output("task_parameters_vis", 'children'),
              [Input("pangenome_hidden", 'children')])
def show_task_parameters(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    return get_task_description_layout(jsonpangenome)

