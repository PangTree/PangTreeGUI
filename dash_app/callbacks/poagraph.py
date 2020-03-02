import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.app import draw_poagraph
from dash_app.components import poagraph
from dash_app.components import visualisation
from dash_app.server import app


@app.callback([Output("full_pangenome_graph", "figure"),
               Output("visualisation_session_info", "data")],
              [Input("pangenome_upload", "contents")])
def get_full_pangenome_graph(pangenome_upload_contents):
    if not pangenome_upload_contents:  # or not draw_poagraph:
        raise PreventUpdate()
    jsonpangenome = visualisation.read_pangenome_upload(pangenome_upload_contents)
    full_pangenome_graph = poagraph.get_pangenome_figure_faster(jsonpangenome)
    hashed_contents = visualisation.get_hash(pangenome_upload_contents)
    return full_pangenome_graph, hashed_contents


@app.callback(Output("elements_cache_info", "data"),
              [Input("visualisation_session_info", "data")],
              [State("elements_cache_info", "data")])
def update_elements_cache_info(visualisation_session_info, elements_cache_info):
    if not visualisation_session_info or not draw_poagraph:
        raise PreventUpdate()
    if elements_cache_info:
        poagraph.remove_elements_data_faster(elements_cache_info)
    new_elem_cache_info = visualisation.get_elem_cache_info(int(visualisation_session_info))
    return str(new_elem_cache_info)


@app.callback(Output("poagraph", "elements"),
              [Input("elements_cache_info", "data"),
               Input("full_pangenome_graph", "relayoutData")],
              [State("pangenome_upload", "contents"),
               State("poagraph", "elements")])
def get_poagraph_elements(elements_cache_info, relayout_data, pangenome_upload_contents, poagraph_elements):

    ignore_trigger = not dash.callback_context.triggered or not elements_cache_info or \
                     not pangenome_upload_contents or not relayout_data  # or not draw_poagraph

    if ignore_trigger:
        raise PreventUpdate

    trigger = dash.callback_context.triggered[0]
    if trigger["prop_id"] == "elements_cache_info" + ".data":
        jsonpangenome = visualisation.read_pangenome_upload(pangenome_upload_contents)
        poagraph.update_cached_poagraph_elements_faster(elements_cache_info, jsonpangenome)

    return poagraph.get_poagraph_elements_faster(elements_cache_info, relayout_data)


@app.callback(Output("full_pangenome_graph", "style"),
              [Input("full_pangenome_graph", "figure")],
              [State("full_pangenome_graph", "style")])
def expand_graph(fig, s):
    if not fig:
        raise PreventUpdate()
    if not s:
        s = {}
    s["visibility"] = "visible"
    return s
