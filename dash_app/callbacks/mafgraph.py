from dash_app.components import tools
from ..server import app
from dash.dependencies import Input, Output, State
from ..layout.layout_ids import *
from ..components import mafgraph


@app.callback(Output(id_mafgraph_graph, 'elements'),
              [Input(id_pangenome_hidden, 'children')],
              [State(id_mafgraph_graph, 'elements')])
def show_input_vis(jsonified_pangenome, mafgraph_elements):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    mafgraph_nodes, mafgraph_edges = mafgraph.get_graph_elements(jsonpangenome)
    mafgraph_elements = []
    mafgraph_elements.extend(mafgraph_nodes)
    mafgraph_elements.extend(mafgraph_edges)
    return mafgraph_elements

@app.callback(
    Output(id_mafgraph_graph, 'style'),
    [Input(id_mafgraph_graph, 'elements')],
    [State(id_mafgraph_graph, 'style')])
def show_mafgraph(mafgraph_elements, mafgraph_style):
    if len(mafgraph_elements) > 0:
        mafgraph_style['visibility'] = 'visible'
    return mafgraph_style
