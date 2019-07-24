from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_app.components import poagraph
import dash
from ..components import tools, visualisation
from ..layout.layout_ids import *

from ..server import app
from time import time
from ..app import draw_poagraph
@app.callback(Output(id_full_pangenome_graph, 'figure'),
              [Input(id_pangenome_upload, 'contents')])
def get_full_pangenome_graph(pangenome_upload_contents):
    if not pangenome_upload_contents or not draw_poagraph:
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
    if not visualisation_session_info or not draw_poagraph:
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
    if not dash.callback_context.triggered or not elements_cache_info or not pangenome_upload_contents or not relayout_data or not draw_poagraph:
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


@app.callback(Output(id_full_pangenome_graph, 'style'),
              [Input(id_full_pangenome_graph, 'figure')],
              [State(id_full_pangenome_graph, 'style')])
def expand_graph(fig, s):
    if not fig:
        raise PreventUpdate()
    print("działam")
    if not s:
        s = {}
    s["visibility"] = "visible"
    return s