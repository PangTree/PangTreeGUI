import pandas as pd
from typing import List

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.components import tools, poagraph
from dash_app.layout.pages import get_task_description_layout
from dash_app.server import app


@app.callback(
    [Output("pangenome_hidden", 'children'),
     Output("poagraph_dropdown", "options"),
     Output("pangviz_load_row", "style")],
    [Input("pangenome_upload", 'contents')])
def load_visualisation(pangenome_content):
    if not pangenome_content:
        raise PreventUpdate()

    json_data = tools.read_upload(pangenome_content)
    alignment_object = poagraph.alignment_main_object
    alignment_object.update_data(json_data)
    options = [{'label': s, 'value': s} for s in alignment_object.sequences.keys()]

    if pangenome_content.startswith("data:application/json;base64"):
        return tools.decode_content(pangenome_content), options, {"visibility": "hidden"}
    return pangenome_content, options, {"visibility": "hidden"}


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

