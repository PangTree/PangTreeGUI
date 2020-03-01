from dash.dependencies import Input, Output, State

from dash_app.components import mafgraph, tools
from dash_app.server import app


@app.callback(Output("mafgraph_graph", 'elements'),
              [Input("pangenome_hidden", 'children')],
              [State("mafgraph_graph", 'elements')])
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
    Output("mafgraph_graph", 'style'),
    [Input("mafgraph_graph", 'elements')],
    [State("mafgraph_graph", 'style')])
def show_mafgraph(mafgraph_elements, mafgraph_style):
    if len(mafgraph_elements) > 0:
        mafgraph_style['visibility'] = 'visible'
    return mafgraph_style
