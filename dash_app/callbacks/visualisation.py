import pandas as pd
from typing import List

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.components import tools, poagraph
from dash_app.layout.pages import get_task_description_layout
from dash_app.server import app


@app.callback(
    Output("pangenome_hidden", 'children'),
    [Input("pangenome_upload", 'contents')])
def load_visualisation(pangenome_content: str) -> str:
    if not pangenome_content:
        raise PreventUpdate()
    if pangenome_content.startswith("data:application/json;base64"):
        return tools.decode_content(pangenome_content)
    return pangenome_content


@app.callback(
    Output("pangviz_result_collapse", 'is_open'),
    [Input("pangenome_upload", 'contents')])
def show_visualisation(pangenome_content: str) -> str:
    if not pangenome_content or not pangenome_content.startswith("data:application/json;base64"):
        return False
    return True


@app.callback(Output("task_parameters_vis", 'children'),
              [Input("pangenome_hidden", 'children')])
def show_task_parameters(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    return get_task_description_layout(jsonpangenome)


# @app.callback(
#     Output("poagraph", 'stylesheet'),
#     [Input("pangenome_hidden", 'children'),
#      Input("partial_consensustable_hidden", 'children')],
#     [State("poagraph_container", 'children')]
# )
# def update_poagraph_stylesheet(jsonified_pangenome: str, jsonified_partial_consensustable,
#                                stylesheet: List) -> List:
#     if not jsonified_pangenome or not jsonified_partial_consensustable:
#         return []
#     jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
#     if not jsonpangenome.affinitytree:
#         return []
#     partial_consensustable_data = pd.read_json(jsonified_partial_consensustable)
#     current_consensuses_names = [column_name for column_name in list(partial_consensustable_data) if
#                                  "CONSENSUS" in column_name]
#     colors = poagraph.get_distinct_colors(len(jsonpangenome.affinitytree))
#     stylesheet = poagraph.get_poagraph_stylesheet()
#     for i, consensus in enumerate(jsonpangenome.affinitytree):
#         if consensus.name in current_consensuses_names:
#             stylesheet.append(
#                 {
#                     'selector': f'.c{consensus.name}',
#                     'style': {
#                         'line-color': f'rgb{colors[i]}',
#                     }
#                 }
#             )
#         else:
#             stylesheet.append(
#                 {
#                     'selector': f'.c{consensus.name}',
#                     'style': {
#                         'line-color': f'rgb{colors[i]}',
#                         'display': 'none'
#                     }
#                 }
#             )
#     return stylesheet
