from typing import List

from dash.exceptions import PreventUpdate
from ..server import app
from dash.dependencies import Input, Output, State
from ..layout.layout_ids import *
from ..layout.pages import get_task_description_layout
from ..components import tools, poagraph


@app.callback(
    Output(id_pangenome_hidden, 'children'),
    [Input(id_pangenome_upload, 'contents')])
def load_visualisation(pangenome_content: str) -> str:
    if not pangenome_content:
        raise PreventUpdate()
    if pangenome_content.startswith("data:application/json;base64"):
        return tools.decode_content(pangenome_content)
    return pangenome_content

@app.callback(
    Output(id_pangviz_result_collapse, 'is_open'),
    [Input(id_pangenome_upload, 'contents')])
def show_visualisation(pangenome_content: str) -> str:
    if not pangenome_content:
        return False
    return True

@app.callback(Output(id_task_parameters_vis, 'children'),
              [Input(id_pangenome_hidden, 'children')])
def show_task_parameters(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    return get_task_description_layout(jsonpangenome)

@app.callback(
    Output(id_poagraph, 'stylesheet'),
    [Input(id_pangenome_hidden, 'children'),
     Input(id_partial_consensustable_hidden, 'children')],
    [State(id_poagraph_container, 'children')]
)
def update_poagraph_stylesheet(jsonified_pangenome: str, jsonified_partial_consensustable, stylesheet: List) -> List:
    if not jsonified_pangenome or not jsonified_partial_consensustable:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(jsonified_pangenome)
    if not jsonpangenome.consensuses:
        return []
    partial_consensustable_data = tools.unjsonify_df(jsonified_partial_consensustable)
    current_consensuses_names = [column_name for column_name in list(partial_consensustable_data) if
                                 "CONSENSUS" in column_name]
    colors = poagraph.get_distinct_colors(len(jsonpangenome.consensuses))
    stylesheet = poagraph.get_poagraph_stylesheet()
    for i, consensus in enumerate(jsonpangenome.consensuses):
        if consensus.name in current_consensuses_names:
            stylesheet.append(
                {
                    'selector': f'.c{consensus.name}',
                    'style': {
                        'line-color': f'rgb{colors[i]}',
                    }
                }
            )
        else:
            stylesheet.append(
                {
                    'selector': f'.c{consensus.name}',
                    'style': {
                        'line-color': f'rgb{colors[i]}',
                        'display': 'none'
                    }
                }
            )
    return stylesheet
