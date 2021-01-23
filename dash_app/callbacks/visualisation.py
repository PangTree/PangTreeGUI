import pandas as pd
import json
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.components import consensustable, consensustree, tools, poagraph
from dash_app.layout.pages import get_task_description_layout
from dash_app.server import app


@app.callback(
    [Output("pangenome_hidden", 'children'),
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
        return tools.decode_content(pangenome_content), {"visibility": "hidden"}
    return pangenome_content, {"visibility": "hidden"}


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

@app.callback(
    Output("poagraph_dropdown", "options"),
    [Input("consensus_tree_graph", 'clickData'),
     Input("poagraph_node_dropdown", "value")],
    [State("full_consensustable_hidden", 'children'),
     State("full_consensustree_hidden", 'children')]
)
def update_poagraph_options(click_data, node_value, consensustable_data, consensustree_data):
    if node_value or click_data:
        if node_value:
            node_id = int(node_value[5:])
        else:
            node_id = click_data['points'][0]['pointIndex']
        full_consensustable = pd.read_json(consensustable_data)
        consensustree_data = json.loads(consensustree_data)
        tree = consensustree.dict_to_tree(consensustree_data)
        node_details_df = consensustable.get_consensus_details_df(node_id, full_consensustable, tree)
        options = [{'label': s, 'value': s} for s in node_details_df["SEQID"].tolist()] 
    else:
        alignment_object = poagraph.alignment_main_object
        if poagraph.alignment_main_object.sequences:
            options = [{'label': s, 'value': s} for s in alignment_object.sequences.keys()]
        else:
            options = []
    return options