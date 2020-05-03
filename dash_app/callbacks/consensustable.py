import json

import pandas as pd
from dash.dependencies import Input, Output, State
from dash_app.components import consensustable, consensustree
from dash_app.server import app
from pangtreebuild.serialization.json import str_to_PangenomeJSON


@app.callback(
    Output("full_consensustable_hidden", 'children'),
    [Input("pangenome_hidden", 'children')])
def update_full_consensustable_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = str_to_PangenomeJSON(jsonified_pangenome)
    consensustable_data = consensustable.get_full_table_data(jsonpangenome)
    return consensustable_data.to_json()


@app.callback(
    Output("partial_consensustable_hidden", 'children'),
    [Input("full_consensustable_hidden", 'children'),
     Input("full_consensustree_hidden", 'children'),
     Input("consensus_tree_slider", 'value')])
def update_partial_table_data(jsonified_full_consensustable: str, jsonified_tree: str,
                              slider_value: float):
    if not jsonified_full_consensustable or not jsonified_tree:
        return []
    full_consensustable_data = pd.read_json(jsonified_full_consensustable)
    full_consensustree_data = json.loads(jsonified_tree)
    full_consensustree_tree = consensustree.dict_to_tree(full_consensustree_data)
    table_without_consensuses_smaller_than_slider = consensustable.remove_smaller_than_slider(
        full_consensustable_data,
        full_consensustree_tree,
        slider_value)
    return table_without_consensuses_smaller_than_slider.to_json()


@app.callback(
    [Output("consensuses_table", 'data'),
     Output("consensuses_table", 'columns'),
     Output("consensuses_table", 'style_data_conditional')],
    [Input("partial_consensustable_hidden", 'children')],
    [State("full_consensustree_hidden", 'children')])
def update_consensus_table(jsonified_partial_consensustable, jsonified_consensus_tree):
    if not jsonified_partial_consensustable:
        return [], [{}], []
    partial_consensustable_data = pd.read_json(jsonified_partial_consensustable)
    consensustable_columns = [{"name": i, "id": i} for i in partial_consensustable_data.columns]
    consensustable_content = partial_consensustable_data.to_dict("rows")

    if not jsonified_consensus_tree:
        return consensustable_content, consensustable_columns, []
    consensustree_data = json.loads(jsonified_consensus_tree)
    tree = consensustree.dict_to_tree(consensustree_data)
    color_cells = consensustable.get_cells_styling(tree, partial_consensustable_data)
    return consensustable_content, consensustable_columns, color_cells


@app.callback(
    Output("consensus_table_container", 'style'),
    [Input("full_consensustable_hidden", 'children')])
def show_consensus_tree_container(jsonified_current_consensustree):
    if jsonified_current_consensustree:
        return {'display': 'block'}
    return {'display': 'none'}
