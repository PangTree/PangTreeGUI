import json
import pandas as pd
from dash.dependencies import Input, Output

from dash_app.components import consensustable, consensustree, tools
from dash_app.server import app


@app.callback(
    Output("full_consensustree_hidden", 'children'),
    [Input("pangenome_hidden", 'children')]
)
def update_consensustree_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    consensustree_dict = consensustree.get_consensustree_dict(jsonpangenome)
    return json.dumps(consensustree_dict)


@app.callback(
    Output("current_consensustree_hidden", 'children'),
    [Input("full_consensustree_hidden", 'children')]
)
def update_current_tree_state(jsonified_full_consensustree):
    if not jsonified_full_consensustree:
        return []
    full_consensustree_data = json.loads(jsonified_full_consensustree)
    full_consensus_tree = consensustree.dict_to_tree(full_consensustree_data)
    current_consensustree_data = consensustree.tree_to_dict(full_consensus_tree)
    return json.dumps(current_consensustree_data)


@app.callback(
    Output("consensus_tree_graph", 'figure'),
    [Input("current_consensustree_hidden", 'children'),
     Input("consensus_tree_slider", 'value'),
     Input("leaf_info_dropdown", 'value'),
     Input("full_consensustable_hidden", 'children')])
def to_consensustree_graph(jsonified_current_consensustree, slider_value, leaf_info,
                           jsonified_full_consensustable):
    if not jsonified_current_consensustree or not jsonified_full_consensustable:
        return {}
    current_consensustree_data = json.loads(jsonified_current_consensustree)
    current_consensustree_tree = consensustree.dict_to_tree(current_consensustree_data)
    full_consensustable_data = pd.read_json(jsonified_full_consensustable)
    return consensustree.get_consensustree_graph(current_consensustree_tree, slider_value,
                                                 leaf_info, full_consensustable_data)


@app.callback(
    Output("consensus_node_details_header", 'children'),
    [Input("consensus_tree_graph", 'clickData')]
)
def to_consensus_node_details_header(tree_click_data):
    if not tree_click_data:
        return []
    clicked_node = tree_click_data['points'][0]
    node_id = clicked_node['pointIndex']
    return f"Consensus {node_id}"


@app.callback(
    Output("consensus_node_details_table_hidden", 'children'),
    [Input("consensus_tree_graph", 'clickData'),
     Input("full_consensustable_hidden", 'children'),
     Input("full_consensustree_hidden", 'children')]
)
def to_consensus_node_details_table(tree_click_data, jsonified_full_consensustable,
                                    jsonified_consensustree):
    if not jsonified_full_consensustable or not tree_click_data:
        return []
    clicked_node = tree_click_data['points'][0]
    node_id = clicked_node['pointIndex']
    full_consensustable = pd.read_json(jsonified_full_consensustable)
    consensustree_data = json.loads(jsonified_consensustree)
    tree = consensustree.dict_to_tree(consensustree_data)
    node_details_df = consensustable.get_consensus_details_df(node_id, full_consensustable, tree)
    return node_details_df.to_json()


@app.callback(
    Output("consensus_node_details_table", 'data'),
    [Input("consensus_node_details_table_hidden", 'children')]
)
def to_consensusnode_details_content(jsonified_consensus_details_table):
    if not jsonified_consensus_details_table:
        return []
    consensus_details_table_data = pd.read_json(jsonified_consensus_details_table)
    return consensus_details_table_data.to_dict("rows")


@app.callback(
    Output("consensus_node_details_distribution", 'src'),
    [Input("consensus_tree_graph", 'clickData'),
     Input("full_consensustable_hidden", 'children')]
)
def to_consensus_node_details_distribution(tree_click_data, jsonified_full_consensustable):
    if not jsonified_full_consensustable or not tree_click_data:
        return ""
    clicked_node = tree_click_data['points'][0]
    node_id = clicked_node['pointIndex']
    full_consensustable = pd.read_json(jsonified_full_consensustable)
    distribution_figure = consensustable.get_node_distribution_fig(node_id, full_consensustable)
    return distribution_figure


@app.callback(
    Output("consensus_node_details_table", 'columns'),
    [Input("consensus_node_details_table_hidden", 'children')]
)
def update_columns(jsonified_consensus_details_table):
    if not jsonified_consensus_details_table:
        return [{}]
    consensus_details_table_data = pd.read_json(jsonified_consensus_details_table)
    return [{"name": i, "id": i} for i in list(consensus_details_table_data.columns)]


@app.callback(
    Output("consensus_tree_container", 'style'),
    [Input("current_consensustree_hidden", 'children')])
def show_consensus_tree_container(jsonified_current_consensustree):
    if jsonified_current_consensustree:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('tree_info', 'style'),
    [Input("consensus_tree_graph", 'clickData')])
def show_consensus_tree_info(click_data):
    if click_data:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output("leaf_info_dropdown", 'options'),
    [Input("full_consensustable_hidden", 'children')])
def to_consensustree_leaf_info_options_dropdown(jsonified_full_consensustable):
    if not jsonified_full_consensustable:
        return []
    full_consensustable = pd.read_json(jsonified_full_consensustable)
    metadata = consensustable.get_metadata_list(full_consensustable)
    return consensustree.get_leaf_info_dropdown_options(metadata)
