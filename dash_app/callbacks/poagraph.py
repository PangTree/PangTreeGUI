from dash.dependencies import Input, Output, State

from dash_app.components import multialignmentgraph, poagraph
from ..components import jsontools
from ..layout.layout_ids import *

from ..server import app

@app.callback(
    Output(id_poagraph, 'elements'),
    [Input(id_poagraph_hidden, 'children')],
    [State(id_poagraph, 'elements')]
)
def update_poagraph(jsonified_poagraph_data: str, elements):
    return []
    if not jsonified_poagraph_data:
        return []
    nodes_data = jsontools.unjsonify_df(jsonified_poagraph_data[0]['props']['children'])
    edges_data = jsontools.unjsonify_df(jsonified_poagraph_data[1]['props']['children'])
    elements += poagraph.get_cytoscape_graph(nodes_data, edges_data)
    return elements


@app.callback(
    Output(id_full_pangenome_graph, 'figure'),
    [Input(id_poagraph_hidden, 'children')],
    [State(id_pangenome_hidden, 'children')]
)
def update_poagraph(jsonified_poagraph_data: str, jsonified_pangenome):
    if not jsonified_poagraph_data or not jsonified_pangenome:
        return []
    jsonpangenome = jsontools.unjsonify_jsonpangenome(jsonified_pangenome)
    nodes_data = jsontools.unjsonify_df(jsonified_poagraph_data[0]['props']['children'])
    edges_data = jsontools.unjsonify_df(jsonified_poagraph_data[1]['props']['children'])
    pangenome_graph = poagraph.get_pangenome_graph(nodes_data, edges_data, jsonpangenome)
    return pangenome_graph

@app.callback(
    Output("tools_poagraph_section", 'style'),
    [Input(id_poagraph_hidden, 'children')])
def show_poagraph(jsonified_poagraph_data):
    if jsonified_poagraph_data:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# @app.callback(
#     Output(id_full_pangenome_graph, 'style'),
#     [Input(id_poagraph_hidden, 'children')])
# def show_poagraph(jsonified_poagraph_data):
#     if not jsonified_poagraph_data:
#         return []
#     nodes_data = jsontools.unjsonify_df(jsonified_poagraph_data[0]['props']['children'])
#     m = nodes_data['x_2'].max()
#     if m < 1000:
#         w = "auto"
#     else:
#         w = f'{10000}px'
#     return {'width': w}
