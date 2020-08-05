import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.app import draw_poagraph
from dash_app.components import poagraph, visualisation, tools
from dash_app.server import app


@app.callback([Output("full_pangenome_graph", "figure"),
               Output("visualisation_session_info", "data"),
               Output("elements_cache_info", "data")],
              [Input("pangenome_upload", "contents")],
              [State("elements_cache_info", "data"),
               State("full_pangenome_graph", "figure")])
def get_full_pangenome_graph(pangenome_upload_contents, cache_info, full_graph):
    if full_graph or not pangenome_upload_contents:
        raise PreventUpdate()
    json_data = tools.read_upload(pangenome_upload_contents)
    poagraph.alignment_main_object.update_data(json_data)
    pangenome_gap_graph = poagraph.alignment_main_object.get_gap_graph()
    
    if cache_info:
        poagraph.remove_elements_data_faster(cache_info)
    hashed_contents = visualisation.get_hash(pangenome_upload_contents)
    new_cache_info = visualisation.get_elem_cache_info(int(hashed_contents))
    return pangenome_gap_graph, hashed_contents, str(new_cache_info)


# @app.callback(Output("poagraph", "figure"),
#               [Input("elements_cache_info", "data"),
#                Input("full_pangenome_graph", "relayoutData")],
#               [State("pangenome_upload", "contents"),
#                State("poagraph", "figure")])
# def get_poagraph_figure(elements_cache_info, relayout_data, pangenome_upload_contents, poagraph_figure):
    
#     if pangenome_upload_contents and not poagraph_figure:
#         json_data = tools.read_upload(pangenome_upload_contents)
#         graph_alignment = poagraph.GraphAlignment(json_data)
#         return poagraph.get_poagraph_fragment(graph_alignment, 0, 50)

#     if relayout_data and "shapes[0].x0" in relayout_data.keys():
#         x0 = int(relayout_data["shapes[0].x0"])
#         x1 = int(relayout_data["shapes[0].x1"])

#         json_data = tools.read_upload(pangenome_upload_contents)
#         graph_alignment = poagraph.GraphAlignment(json_data)
#         print(f"{x0}, {x1}")
#         return poagraph.get_poagraph_fragment(graph_alignment, x0, min(x1, x0+50))
#     raise dash.exceptions.PreventUpdate()
    

