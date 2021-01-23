import json
import pandas as pd
from dash.dependencies import Input, Output

from dash_app.components import consensustable, consensustree, tools
from dash_app.app import app


@app.callback(
    Output("full_consensustree_hidden", 'children'),
    [
        Input("pangenome_hidden", 'children')
    ]
)
def update_consensustree_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    consensustree_dict = consensustree.get_consensustree_dict(jsonpangenome)
    return json.dumps(consensustree_dict)


@app.callback(
    Output("current_consensustree_hidden", 'children'),
    [
        Input("full_consensustree_hidden", 'children')
    ]
)
def update_current_tree_state(jsonified_full_consensustree):
    if not jsonified_full_consensustree:
        return []
    full_consensustree_data = json.loads(jsonified_full_consensustree)
    full_consensus_tree = consensustree.dict_to_tree(full_consensustree_data)
    current_consensustree_data = consensustree.tree_to_dict(full_consensus_tree)
    return json.dumps(current_consensustree_data)


@app.callback(
    [
        Output("consensus_tree_graph", 'figure'),
        Output("consensus_tree_slider", 'min'),
        Output("consensus_tree_slider", 'marks')
    ],
    [
        Input("current_consensustree_hidden", 'children'),
        Input("leaf_info_dropdown", 'value'),
        Input("full_consensustable_hidden", 'children')
    ]
)
def to_consensustree_graph(jsonified_current_consensustree, leaf_info,
                           jsonified_full_consensustable):
    if not jsonified_current_consensustree or not jsonified_full_consensustable:
        return {}, 0, {}
    current_consensustree_data = json.loads(jsonified_current_consensustree)
    current_consensustree_tree = consensustree.dict_to_tree(current_consensustree_data)
    full_consensustable_data = pd.read_json(jsonified_full_consensustable)
    return consensustree.get_consensustree_graph(current_consensustree_tree, leaf_info, full_consensustable_data)


@app.callback(
    Output("leaf_info_dropdown", 'options'),
    [
        Input("full_consensustable_hidden", 'children')
    ]
)
def to_consensustree_leaf_info_options_dropdown(jsonified_full_consensustable):
    if not jsonified_full_consensustable:
        return []
    full_consensustable = pd.read_json(jsonified_full_consensustable)
    metadata = consensustable.get_metadata_list(full_consensustable)
    return consensustree.get_leaf_info_dropdown_options(metadata)
