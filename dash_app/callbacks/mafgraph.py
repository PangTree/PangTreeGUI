from dash_app.components import jsontools
from ..server import app
from dash.dependencies import Input, Output, State
from ..layout.layout_ids import *


@app.callback(
    Output(id_mafgraph_graph, 'elements'),
    [Input(id_mafgraph_hidden, 'children')],
    [State(id_mafgraph_graph, 'elements')]
)
def update_poagraph(jsonified_mafgraph_elements: str, elements):
    if not jsonified_mafgraph_elements:
        return []

    nodes = jsontools.unjsonify_builtin_types(jsonified_mafgraph_elements[0]['props']['children'])
    edges = jsontools.unjsonify_builtin_types(jsonified_mafgraph_elements[1]['props']['children'])
    elements = []
    elements.extend(nodes)
    elements.extend(edges)
    return elements

@app.callback(
    Output(id_mafgraph_graph, 'style'),
    [Input(id_mafgraph_graph, 'elements')],
    [State(id_mafgraph_graph, 'style')])
def show_mafgraph(mafgraph_elements, mafgraph_style):
    if len(mafgraph_elements) > 0:
        mafgraph_style['visibility'] = 'visible'
    return mafgraph_style