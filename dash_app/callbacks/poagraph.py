from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.components import visualisation
from dash_app.server import app


@app.callback([Output("visualisation_session_info", "data"),
               Output("elements_cache_info", "data")],
              [Input("pangenome_upload", "contents")],
              [State("elements_cache_info", "data"),
               State("full_pangenome_graph", "figure")])
def get_full_pangenome_graph(pangenome_upload_contents, cache_info, full_graph):
    if full_graph or not pangenome_upload_contents:
        raise PreventUpdate()
    
    hashed_contents = visualisation.get_hash(pangenome_upload_contents)
    new_cache_info = visualisation.get_elem_cache_info(int(hashed_contents))
    return hashed_contents, str(new_cache_info)

@app.callback(Output("poagraph_checklist", "value"),
              [Input("poagraph-slider", "value")],
              [State("poagraph_checklist", "value")])
def check_checklist(slider, checklist):
    if slider > 40 and 1 not in checklist:
        checklist.append(1)
    if slider > 55 and 2 not in checklist:
        checklist.append(2)
    return checklist
 