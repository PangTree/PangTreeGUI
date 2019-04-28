from typing import Dict, List

from dash.dependencies import Input, Output, State

from dash_app.components import parameters, consensustable, consensustree, multialignmentgraph, poagraph, mafgraph
import dash_html_components as html
import dash_app.components.jsontools as jsontools
from ..layout.layout_ids import *
from ..components import poagraph as poagraph_component

from ..server import app


@app.callback(
    Output(id_full_consensustable_hidden, 'children'),
    [Input(id_pangenome_hidden, 'children')]
)
def update_full_consensustable_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = jsontools.unjsonify_jsonpangenome(jsonified_pangenome)
    consensustable_data = consensustable.get_full_table_data(jsonpangenome)
    return jsontools.jsonify_df(consensustable_data)


@app.callback(
    Output(id_full_consensustree_hidden, 'children'),
    [Input(id_pangenome_hidden, 'children')]
)
def update_consensustree_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = jsontools.unjsonify_jsonpangenome(jsonified_pangenome)
    consensustree_dict = consensustree.get_consensustree_dict(jsonpangenome)
    return jsontools.jsonify_builtin_types(consensustree_dict)


@app.callback(
    Output(id_poagraph_hidden, 'children'),
    [Input(id_pangenome_hidden, 'children')],
)
def update_poagraph_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = jsontools.unjsonify_jsonpangenome(jsonified_pangenome)
    pangenome, poagraph_nodes, poagraph_edges = poagraph.get_data(jsonpangenome)
    return [html.Div(jsontools.jsonify_builtin_types(pangenome)),
            html.Div(jsontools.jsonify_builtin_types(poagraph_nodes)),
            html.Div(jsontools.jsonify_builtin_types(poagraph_edges))]


@app.callback(
    Output(id_poagraph, 'stylesheet'),
    [Input(id_pangenome_hidden, 'children'),
     Input(id_partial_consensustable_hidden, 'children')],
    [State(id_poagraph_container, 'children')]
)
def update_poagraph_stylesheet(jsonified_pangenome: str, jsonified_partial_consensustable, stylesheet: List) -> List:
    if not jsonified_pangenome or not jsonified_partial_consensustable:
        return {}
    jsonpangenome = jsontools.unjsonify_jsonpangenome(jsonified_pangenome)
    if not jsonpangenome.consensuses:
        return {}
    partial_consensustable_data = jsontools.unjsonify_df(jsonified_partial_consensustable)
    current_consensuses_names = [column_name for column_name in list(partial_consensustable_data) if "CONSENSUS" in column_name]
    colors = poagraph.get_distinct_colors(len(jsonpangenome.consensuses))
    s = poagraph_component.get_poagraph_stylesheet()
    for i, consensus in enumerate(jsonpangenome.consensuses):
        if consensus.name in current_consensuses_names:
            s.append(
                {
                    'selector': f'.c{consensus.name}',
                    'style': {
                        'line-color': f'rgb{colors[i]}',
                    }
                }
            )
        else:
            s.append(
                {
                    'selector': f'.c{consensus.name}',
                    'style': {
                        'line-color': f'rgb{colors[i]}',
                        'display': 'none'
                    }
                }
            )
    return s

@app.callback(
    Output(id_mafgraph_hidden, 'children'),
    [Input(id_pangenome_hidden, 'children')]
)
def update_mafgraph_hidden(jsonified_pangenome):
    if not jsonified_pangenome:
        return []
    jsonpangenome = jsontools.unjsonify_jsonpangenome(jsonified_pangenome)
    mafgraph_nodes, mafgraph_edges = mafgraph.get_graph_elements(jsonpangenome)
    return [html.Div(jsontools.jsonify_builtin_types(mafgraph_nodes)),
            html.Div(jsontools.jsonify_builtin_types(mafgraph_edges))]
