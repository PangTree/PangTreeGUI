from dash.exceptions import PreventUpdate
from ..server import app
from dash.dependencies import Input, Output, State
from ..layout.layout_ids import *
from ..components import tools, visualisation, mafgraph, poagraph
import dash_html_components as html


@app.callback(
    Output(id_pangenome_hidden, 'children'),
    [Input(id_pangenome_upload, 'contents')])
def load_visualisation(pangenome_content: str) -> str:
    if not pangenome_content:
        raise PreventUpdate()
    if pangenome_content.startswith("data:application/json;base64"):
        return tools.decode_content(pangenome_content)
    return pangenome_content

@app.callback(Output(id_task_parameters_vis, 'children'),
              [Input(id_pangenome_hidden, 'children')])
def show_task_parameters(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    if not jsonpangenome.task_parameters:
        return []
    return visualisation.get_task_params(jsonpangenome.task_parameters)

@app.callback(Output(id_input_info_vis, "children"),
[Input(id_pangenome_hidden, 'children')])
def show_input_info(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    return visualisation.get_input_info(jsonpangenome)


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


@app.callback(
    Output(id_poagraph_hidden, 'children'),
    [Input(id_pangenome_hidden, 'children')],
)
def update_poagraph_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    pangenome, poagraph_nodes, poagraph_edges = poagraph.get_data(jsonpangenome)
    return [html.Div(tools.jsonify_builtin_types(pangenome)),
            html.Div(tools.jsonify_builtin_types(poagraph_nodes)),
            html.Div(tools.jsonify_builtin_types(poagraph_edges))]


@app.callback(
    Output(id_full_pangenome_graph, 'figure'),
    [Input(id_poagraph_hidden, 'children')]
)
def update_pangenome_graph(jsonified_pangenome_data: str):
    if not jsonified_pangenome_data:
        return {}
    pangenome_graph_data = jsonified_pangenome_data[0]['props']['children']
    pangenome_graph = tools.unjsonify_builtin_types(pangenome_graph_data)
    return poagraph.get_pangenome_figure(pangenome_graph)

@app.callback(
    Output(id_poagraph, 'style'),
    [Input(id_poagraph, 'elements')],
    [State(id_poagraph, 'style')])
def show_poagraph(elements, poagraph_style):
    if len(elements) > 0:
        poagraph_style['visibility'] = 'visible'
    return poagraph_style

@app.callback(
    Output(id_poagraph_node_info, 'children'),
    [Input(id_poagraph, 'tapNodeData')])
def show_specific_node_info(clicked_node_data):
    if not clicked_node_data or clicked_node_data['label'] == '':
        raise PreventUpdate()
    return str(clicked_node_data)

@app.callback(
    Output(id_poagraph, 'elements'),
    [Input(id_poagraph_hidden, 'children'),
     Input(id_full_pangenome_graph, 'relayoutData')],
    [State(id_poagraph, 'elements')]
)
def update_poagraph(jsonified_pangenome_data: str, relayoutData, elements):
    if not jsonified_pangenome_data:
        return []
    if len(elements) == 0:
        min_x = None
        max_x = None
    else:
        try:
            min_x = int(relayoutData['xaxis.range[0]'])
            max_x = int(relayoutData['xaxis.range[1]'])
        except KeyError:
            min_x = None
            max_x = None

    nodes = tools.unjsonify_builtin_types(jsonified_pangenome_data[1]['props']['children'])
    edges = tools.unjsonify_builtin_types(jsonified_pangenome_data[2]['props']['children'])
    elements = []
    elements += poagraph.get_poagraph_elements(nodes, edges, min_x, max_x)
    return elements


@app.callback(
    Output("tools_poagraph_section", 'style'),
    [Input(id_poagraph_hidden, 'children')])
def show_poagraph(jsonified_poagraph_data):
    if jsonified_poagraph_data:
        return {'visibility': 'visible'}
    else:
        return {'visibility': 'hidden'}