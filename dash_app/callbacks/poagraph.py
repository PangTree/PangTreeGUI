import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.app import draw_poagraph
from dash_app.components import poagraph, visualisation, tools
from dash_app.server import app


@app.callback([Output("full_pangenome_graph", "figure"),
               Output("visualisation_session_info", "data")],
              [Input("pangenome_upload", "contents")])
def get_full_pangenome_graph(pangenome_upload_contents):
    if not pangenome_upload_contents:  # or not draw_poagraph:
        raise PreventUpdate()
    json_data = tools.read_upload(pangenome_upload_contents)
    graph_alignment = poagraph.GraphAlignment(json_data)
    pangenome_gap_graph = poagraph.get_gap_graph(graph_alignment)
    hashed_contents = visualisation.get_hash(pangenome_upload_contents)
    return pangenome_gap_graph, hashed_contents


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


@app.callback(Output("poagraph", "figure"),
              [Input("elements_cache_info", "data"),
               Input("full_pangenome_graph", "relayoutData")],
              [State("pangenome_upload", "contents"),
               State("poagraph", "figure")])
def get_poagraph_elements(elements_cache_info, relayout_data, pangenome_upload_contents, poagraph_figure):
    # if not (dash.callback_context.triggered and elements_cache_info and pangenome_upload_contents and relayout_data):
    #     raise PreventUpdate
    # trigger = dash.callback_context.triggered[0]
    # if trigger["prop_id"] == "elements_cache_info" + ".data":
    #     jsonpangenome = visualisation.read_pangenome_upload(pangenome_upload_contents)
    #     poagraph.update_cached_poagraph_elements_faster(elements_cache_info, jsonpangenome)
    
    if pangenome_upload_contents and not poagraph_figure:
        json_data = tools.read_upload(pangenome_upload_contents)
        graph_alignment = poagraph.GraphAlignment(json_data)
        return poagraph.get_poagraph_fragment(graph_alignment, 0, 50)

    if relayout_data and "shapes[0].x0" in relayout_data.keys():
        x0 = int(relayout_data["shapes[0].x0"])
        x1 = int(relayout_data["shapes[0].x1"])

        json_data = tools.read_upload(pangenome_upload_contents)
        graph_alignment = poagraph.GraphAlignment(json_data)
        print(f"{x0}, {x1}")
        return poagraph.get_poagraph_fragment(graph_alignment, x0, min(x1, x0+50))
    raise dash.exceptions.PreventUpdate()
    

