from typing import List, Dict, Union, Tuple
import pandas as pd
from poapangenome.output.PangenomeJSON import PangenomeJSON
import plotly.graph_objs as go

y_pos_dict = {'A': 40, 'C': 35, 'G': 30, 'T': 25, 'N': 20, 'W': 10, '?': 5, 'n': 2}

PointsDict = Dict[str, Union[List[int], List[str]]]
Path = Dict[str, Union[List[int], List[str]]]
PathsDict = Dict[int, Path]
PoagraphData = Dict[str, Union[PointsDict, PathsDict]]
CPoagraphData = Tuple[str, str]
#
#
# def get_data(jsonpangenome: PangenomeJSON) -> PoagraphData:
#     poagraph_data: PoagraphData = {"nodes": {"x": [node.column_id for node in jsonpangenome.nodes],
#                                              "y": [y_pos_dict[node.base] for node in jsonpangenome.nodes],
#                                              "base": [node.base for node in jsonpangenome.nodes]},
#                                    "paths": {}}
#
#     for sequence in jsonpangenome.sequences:
#         poagraph_data["paths"][sequence.sequence_int_id] = {
#             "x": [jsonpangenome.nodes[node_id].column_id for node_id in sequence.nodes_ids],
#             "y": [y_pos_dict[jsonpangenome.nodes[node_id].base] for node_id in sequence.nodes_ids],
#             "name": sequence.sequence_str_id
#         }
#
#     return poagraph_data

def get_data(jsonpangenome: PangenomeJSON) -> Tuple[str, str]:
    nodes_data = {'n1': ['C', 10, 20, [0, 1], []],
                  'n2': ['G', 15, 20, [2], [0, 1]],
                  'n3': ['G', 20, 20, [0, 1, 2], [0, 1]]}
    df_nodes = pd.DataFrame.from_dict(nodes_data,
                                      orient='index',
                                      columns=['base', 'x', 'y', 'sequences_ids', 'consensuses_ids'])

    edges_data = {'e1': ['n1', 'n3', [0, 1], []],
                  'e2': ['n2', 'n3', [2], [0, 1]]}
    df_edges = pd.DataFrame.from_dict(edges_data,
                                orient='index',
                                columns=['from', 'to', 'sequences_ids', 'consensuses_ids'])
    return df_nodes.to_json(), df_edges.to_json()


def get_cytoscape_graph(nodes_data, edges_data) -> List[any]: #tu zwracam elements z cytoscape
    def get_node(id, label, x, y, cl):
        return {'data': {'id': id, 'label': label}, 'position': {'x': x, 'y': y}, 'classes': cl}

    def get_c_node(id, x, y, cl):
        return {'data': {'id': id}, 'position': {'x': x, 'y': y}, 'classes': cl}

    def get_edge(id, source, target, weight, cl):
        return {'data': {'source': source, 'target': target, 'weight': weight}, 'classes': cl}
        # return {'data': {'id': id, 'source': source, 'target': target, 'weight': weight}, 'classes': cl}

    nodes = [get_node(i, l, x, y, c) for i, l, x, y, c in [('n1', 'C', 50, 50, 'C s_node'),
                                                           ('n2', 'G', 50, 100, 'G s_node'),
                                                           ('n3', 'G', 80, 75, 'G s_node'),
                                                           ('n4', 'T', 90, 75, 'T s_node'),
                                                           ('n5', 'A', 100, 75, 'A s_node'),
                                                           ('n6', 'A', 130, 50, 'A s_node'),
                                                           ('n7', 'G', 130, 75, 'G s_node'),
                                                           ('n8', 'A', 130, 100, 'A s_node'),
                                                           ('n9', 'A', 160, 50, 'A provided  s_node'),
                                                           ('n10', 'T', 160, 75, 'T s_node'),
                                                           ('n11', 'G', 170, 75, 'G s_node'),
                                                           ('n12', 'A', 200, 75, 'A s_node')]]

    c_nodes = [get_c_node(i, x, y, c) for i, x, y, c in [('cn1', 50, 50, 'c_node'),
                                                         ('cn2', 50, 100, 'c_node'),
                                                         ('cn3', 80, 75, 'c_node'),
                                                         ('cn4', 90, 75, 'c_node'),
                                                         ('cn5', 100, 75, 'c_node'),
                                                         ('cn6', 130, 50, 'c_node'),
                                                         ('cn7', 130, 75, 'c_node'),
                                                         ('cn8', 130, 100, 'c_node'),
                                                         ('cn9', 160, 50, 'c_node'),
                                                         ('cn10', 160, 75, 'c_node'),
                                                         ('cn11', 170, 75, 'c_node'),
                                                         ('cn12', 200, 75, 'c_node')]]

    edges = [get_edge(i, s, t, w, c) for i, s, t, w, c in [('e1', 'n1', 'n3', 2, 's_edge'),
                                                           # ('e2', 'n2', 'n3', 1, 's_edge'),
                                                           ('e3', 'n3', 'n4', 3, 's_edge'),
                                                           ('e4', 'n4', 'n5', 3, 's_edge'),
                                                           ('e5', 'n5', 'n6', 1, 's_edge'),
                                                           ('e6', 'n5', 'n7', 1, 's_edge'),
                                                           ('e7', 'n5', 'n8', 1, 's_edge'),
                                                           ('e8', 'n6', 'n7', 1, 's_edge_aligned'),
                                                           ('e9', 'n7', 'n8', 1, 's_edge_aligned'),
                                                           ('e10', 'n6', 'n9', 1, 's_edge'),
                                                           ('e11', 'n6', 'n10', 1, 's_edge'),
                                                           ('e12', 'n7', 'n10', 1, 's_edge'),
                                                           ('e13', 'n8', 'n12', 1, 's_edge'),
                                                           ('e14', 'n9', 'n12', 1, 's_edge'),
                                                           ('e15', 'n11', 'n12', 1, 's_edge'),

                                                           ('e16', 'cn2', 'cn3', 2, 'c_edge c1'),
                                                           ('e17', 'cn3', 'cn4', 2, 'c_edge c1 c_short'),
                                                           ('e18', 'cn4', 'cn5', 2, 'c_edge c1 c_short'),
                                                           ('e19', 'cn5', 'cn7', 2, 'c_edge c1'),
                                                           ('e21', 'cn10', 'cn11', 2, 'c_edge c1'),
                                                           ('e22', 'cn11', 'cn12', 2, 'c_edge c1'),
                                                           ('e20', 'cn7', 'cn10', 2, 'c_edge c1'),

                                                           ('e21', 'cn2', 'cn3', 2, 'c_edge c2'),
                                                           ('e22', 'cn3', 'cn4', 2, 'c_edge c2 c_short'),
                                                           ('e23', 'cn4', 'cn5', 2, 'c_edge c2 c_short'),
                                                           ('e24', 'cn5', 'cn6', 2, 'c_edge c2'),
                                                           ('e25', 'cn6', 'cn9', 2, 'c_edge c2'),
                                                           ('e26', 'cn9', 'cn12', 2, 'c_edge c2'),

                                                           ]]
    return nodes + c_nodes + edges

def get_scatter_graph(poagraph_data: Dict) -> go.Figure:
    nodes_scatter = get_nodes_scatter(poagraph_data["nodes"])
    scatters = []

    for seqid, sequencegraph_data in poagraph_data["paths"].items():
        scatters.append(get_path_scatter(name=sequencegraph_data["name"],
                                         x_pos=sequencegraph_data["x"],
                                         y_pos=sequencegraph_data["y"]
                                         ))
    scatters.append(nodes_scatter)
    layout = dict(title='Poagraph',
                  annotations=[],
                  font=dict(size=12),
                  showlegend=True,
                  xaxis=go.layout.XAxis(dict(title="Column ID", showline=False, zeroline=False, showgrid=False)),
                  yaxis=go.layout.YAxis(dict(title="Base",
                                             ticktext=[*y_pos_dict.keys()],
                                             tickvals=[*y_pos_dict.values()],
                                             showline=False, zeroline=False, showgrid=False, showticklabels=True,)),
                  margin=dict(l=40, r=40, b=85, t=100),
                  hovermode='closest',
                  plot_bgcolor='rgb(248,248,248)',
                  autosize=True,
                  )

    return go.Figure(
            data=scatters,
            layout=layout
            )

def get_nodes_scatter(nodes_poagraph_data) -> go.Scatter:
    return go.Scatter(x=nodes_poagraph_data["x"],
                      y=nodes_poagraph_data["y"],
                      text=nodes_poagraph_data["base"],
                      mode="markers+text",
                      marker=dict(
                          symbol="circle",
                          size=20,
                          color='white',
                          line=dict(
                              width=1),
                      ),
                      textfont=dict(
                          size=12,
                          color='rgb(0,0,0)'
                      )
                      )


def get_path_scatter(name: str, x_pos: List[str], y_pos: List[str]) -> go.Scatter:
    return go.Scatter(
        x=x_pos,
        y=y_pos,
        name=name,
        mode='lines',
            line=dict(
                    width=1,
                    color='#404040',
                    shape='spline'
            )
    )


