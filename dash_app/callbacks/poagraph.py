from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_app.components import poagraph
import dash
import dash_html_components as html
from ..components import tools, visualisation
from ..layout.layout_ids import *

from ..server import app
from time import time
@app.callback(Output(id_full_pangenome_graph, 'figure'),
              [Input(id_pangenome_upload, 'contents')])
def get_full_pangenome_graph(pangenome_upload_contents):
    if not pangenome_upload_contents:
        raise PreventUpdate()
    jsonpangenome = visualisation.read_pangenome_upload(pangenome_upload_contents)
    return poagraph.get_pangenome_figure_faster(jsonpangenome)

@app.callback(Output(id_visualisation_session_info, 'data'),
              [Input(id_pangenome_upload, 'contents')])
def update_pangenome_hash(pangenome_upload_contents):
    if not pangenome_upload_contents:
        raise PreventUpdate()
    hashed_contents = visualisation.get_hash(pangenome_upload_contents)
    return hashed_contents

@app.callback(Output(id_elements_cache_info, 'data'),
              [Input(id_visualisation_session_info, 'data')],
              [State(id_elements_cache_info, 'data')])
def update_elements_cache_info(visualisation_session_info, elements_cache_info):
    if not visualisation_session_info:
        raise PreventUpdate()
    if elements_cache_info:
        poagraph.remove_elements_data_faster(elements_cache_info)
    new_elem_cache_info = visualisation.get_elem_cache_info(int(visualisation_session_info))
    print(new_elem_cache_info)
    return str(new_elem_cache_info)


@app.callback(Output(id_poagraph, 'elements'),
              [Input(id_elements_cache_info, 'data'),
               Input(id_full_pangenome_graph, 'relayoutData')],
              [State(id_pangenome_upload, 'contents'),
               State(id_poagraph, 'elements')])
def get_poagraph_elements(elements_cache_info, relayout_data, pangenome_upload_contents, poagraph_elements):
    if not dash.callback_context.triggered or not elements_cache_info or not pangenome_upload_contents or not relayout_data:
        raise PreventUpdate
    trigger = dash.callback_context.triggered[0]
    if trigger['prop_id'] == id_elements_cache_info+'.data':
        print("generuje elementy do ", elements_cache_info)
        jsonpangenome = visualisation.read_pangenome_upload(pangenome_upload_contents)
        start = time()
        poagraph.update_cached_poagraph_elements_faster(elements_cache_info, jsonpangenome)
        end = time()
        print("time" ,str(end-start))
    print("wybieram podzbiór dla", relayout_data, "stąd: ", elements_cache_info)
    poagraph_elements = poagraph.get_poagraph_elements_faster(elements_cache_info, relayout_data)
    return poagraph_elements

# @app.callback(
#     Output(id_poagraph_hidden, 'children'),
#     [Input(id_pangenome_hidden, 'children')],
# )
# def update_poagraph_hidden(jsonified_pangenome):
#     if not jsonified_pangenome:
#         return []
#     jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
#     pangenome, poagraph_nodes, poagraph_edges = poagraph.get_data(jsonpangenome)
#     return [html.Div(tools.jsonify_builtin_types(pangenome)),
#             html.Div(tools.jsonify_builtin_types(poagraph_nodes)),
#             html.Div(tools.jsonify_builtin_types(poagraph_edges))]

# @app.callback(
#     Output(id_poagraph, 'elements'),
#     [Input(id_poagraph_hidden, 'children'),
#      Input(id_full_pangenome_graph, 'relayoutData')],
#     [State(id_poagraph, 'elements')]
# )
# def update_poagraph(jsonified_pangenome_data: str, relayoutData, elements):
#     if not jsonified_pangenome_data:
#         return []
#     if len(elements) == 0:
#         min_x = None
#         max_x = None
#     else:
#         try:
#             min_x = int(relayoutData['xaxis.range[0]'])
#             max_x = int(relayoutData['xaxis.range[1]'])
#         except KeyError:
#             min_x = None
#             max_x = None
#
#     nodes = tools.unjsonify_builtin_types(jsonified_pangenome_data[1]['props']['children'])
#     edges = tools.unjsonify_builtin_types(jsonified_pangenome_data[2]['props']['children'])
#     elements = []
#     elements += poagraph.get_poagraph_elements(nodes, edges, min_x, max_x)
#     return elements


# @app.callback(
#     Output(id_full_pangenome_graph, 'figure'),
#     [Input(id_poagraph_hidden, 'children')]
# )
# def update_pangenome_graph(jsonified_pangenome_data: str):
#     if not jsonified_pangenome_data:
#         return {}
#     pangenome_graph_data = jsonified_pangenome_data[0]['props']['children']
#     pangenome_graph = tools.unjsonify_builtin_types(pangenome_graph_data)
#     return poagraph.get_pangenome_figure(pangenome_graph)

# @app.callback(
#     Output("tools_poagraph_section", 'style'),
#     [Input(id_poagraph_hidden, 'children')])
# def show_poagraph(jsonified_poagraph_data):
#     if jsonified_poagraph_data:
#         return {'visibility': 'visible'}
#     else:
#         return {'visibility': 'hidden'}

# @app.callback(
#     Output(id_poagraph, 'style'),
#     [Input(id_poagraph, 'elements')],
#     [State(id_poagraph, 'style')])
# def show_poagraph(elements, poagraph_style):
#     if len(elements) > 0:
#         poagraph_style['visibility'] = 'visible'
#     return poagraph_style

# @app.callback(
#     Output(id_poagraph_node_info, 'children'),
#     [Input(id_poagraph, 'tapNodeData')])
# def show_specific_node_info(clicked_node_data):
#     if not clicked_node_data or clicked_node_data['label'] == '':
#         raise PreventUpdate()
#     return str(clicked_node_data)

@app.callback(Output(id_full_pangenome_container, 'style'),
              [Input(id_full_pangenome_graph, 'figure')],
              [State(id_full_pangenome_container, 'style')])
def expand_graph(fig, s):
    if not fig:
        raise PreventUpdate()
    print("działam")
    if not s:
        s = {}
    s["visibility"] = "visible"
    return s