from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_app.components import poagraph
import dash
from ..components import tools, visualisation
from ..layout.layout_ids import *

from ..server import app
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
    return str(new_elem_cache_info)


@app.callback(Output(id_poagraph, 'elements'),
              [Input(id_elements_cache_info, 'data'),
               Input(id_full_pangenome_graph, 'relayoutData')],
              [State(id_pangenome_upload, 'contents'),
               State(id_poagraph, 'elements')])
def get_poagraph_elements(elements_cache_info, relayout_data, pangenome_upload_contents, poagraph_elements):
    def new_pangenome_loaded(trigger):
        return trigger['prop_id'] == id_elements_cache_info + '.data'

    def ignore_trigger():
        return not dash.callback_context.triggered or \
               not elements_cache_info or \
               not pangenome_upload_contents or \
               not relayout_data or \
               not draw_poagraph

    def cache_new_poagraph_elements():
        jsonpangenome = visualisation.read_pangenome_upload(pangenome_upload_contents)
        if jsonpangenome.nodes is None:
            return
        poagraph.update_cached_poagraph_elements_faster(elements_cache_info, jsonpangenome)

    def read_poagraph_elements_to_redraw():
        return poagraph.get_poagraph_elements_faster(elements_cache_info, relayout_data)

    if ignore_trigger():
        raise PreventUpdate

    trigger = dash.callback_context.triggered[0]
    if new_pangenome_loaded(trigger):
        cache_new_poagraph_elements()

    return read_poagraph_elements_to_redraw()


@app.callback(Output(id_full_pangenome_graph, 'style'),
              [Input(id_full_pangenome_graph, 'figure')],
              [State(id_full_pangenome_graph, 'style')])
def expand_graph(fig, s):
    if not fig:
        raise PreventUpdate()
    if not s:
        s = {}
    s["visibility"] = "visible"
    return s
