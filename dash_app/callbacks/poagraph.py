from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_app.components import multialignmentgraph, poagraph
from ..components import jsontools
from ..layout.layout_ids import *

from ..server import app


@app.callback(
    Output(id_poagraph, 'elements'),
    [Input(id_poagraph_hidden, 'children'),
     Input(id_full_pangenome_graph, 'relayoutData')],
    [State(id_poagraph, 'elements')]
)
def update_poagraph(jsonified_poagraph_data: str, relayoutData, elements):
    if not jsonified_poagraph_data:
        return []
    if len(elements) == 0:
        min_x = None
        max_x = None
    else:
        try:
            min_x = int(relayoutData['xaxis.range[0]'])
            max_x = int(relayoutData['xaxis.range[1]'])
        except KeyError:
            raise PreventUpdate()

    print("callback", relayoutData)
    nodes_data = jsontools.unjsonify_df(jsonified_poagraph_data[0]['props']['children'])
    # edges_data = jsontools.unjsonify_df(jsonified_poagraph_data[1]['props']['children'])
    elements = []
    elements += poagraph.get_poagraph_elements(nodes_data, min_x, max_x)
    return elements


@app.callback(
    Output(id_full_pangenome_graph, 'figure'),
    [Input(id_poagraph_hidden, 'children')]
)
def update_pangenome_graph(jsonified_pangenome_data: str):
    if not jsonified_pangenome_data:
        return []
    nodes_data = jsontools.unjsonify_df(jsonified_pangenome_data[0]['props']['children'])
    return poagraph.get_pangenome_figure(nodes_data)

@app.callback(
    Output("tools_poagraph_section", 'style'),
    [Input(id_poagraph_hidden, 'children')])
def show_poagraph(jsonified_poagraph_data):
    if jsonified_poagraph_data:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

