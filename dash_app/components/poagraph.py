from collections import namedtuple
from typing import List, Dict, Tuple, Set, Optional
import pandas as pd
from poapangenome.output.PangenomeJSON import PangenomeJSON, Sequence
import plotly.graph_objs as go
from ..layout.css_styles import colors3 as colors

EdgeData = namedtuple('EdgeData', ['to', 'classes'])

NodeData = namedtuple('NodeData', ['base', 'x_detailed', 'y_detailed', 'x_pangenome', 'y_pangenome', 'sequences_ids', 'consensus_ids'])


class PoaGraph:
    def __init__(self, jsonpangenome: PangenomeJSON):
        self.nodes: Dict[int, NodeData] = {}
        self.edges: Dict[int, EdgeData] = {}
        self.edges_reversed: Dict[int, Set[int]] = {}
        self.columns: Dict[int, Set[int]] = {}
        self.continuous_paths: List[List[int]] = []
        self.poagraph_node_width: int = 10
        self.pangenome_space: int = 1

        self.nodes_df = pd.DataFrame.from_records([{
            'id': node.id,
            'base': node.base,
            'x_poagraph': node.column_id * self.poagraph_node_width * 1.5,
            'y_poagraph': -1,
            'x_pangenome': node.column_id,
            'y_pangenome': -1,
            'sequences_ids': [],
            'consensus_ids': [],
            'to_left':[],
            'to_right':[]
        } for node in jsonpangenome.nodes], index='id')

        for sequence in jsonpangenome.sequences:
            for path in sequence.nodes_ids:
                path_end = len(path) - 1
                for i, node_id in enumerate(path):

                    self.nodes_df.at[node_id, 'sequences_ids'].append(sequence.sequence_int_id)
                    if i != 0:
                        self.nodes_df.at[node_id, 'to_left'].append(path[i-1])
                    if i < path_end:
                        self.nodes_df.at[node_id, 'to_right'].append(path[i+1])


    def _find_continuous_paths(self) -> List[List[int]]:
        continuous_paths = []

        for node_id, node in self.nodes_df.iterrows():
            following_nodes_ids = list(set(node.to_right))
            if len(following_nodes_ids) != 1:
                continue
            single_following_node_id = following_nodes_ids[0]
            other_incoming_nodes = list(set(self.nodes_df.loc[single_following_node_id, 'to_left']))
            if len(other_incoming_nodes) != 1:
                continue
            # self.edges[node_id].classes.append("s_short")
            path_was_extended = False

            for continuous_path in continuous_paths:
                if continuous_path[-1] == node_id:
                    continuous_path.append(single_following_node_id)
                    path_was_extended = True
                    break
            if not path_was_extended:
                continuous_paths.append([node_id, single_following_node_id])

        return continuous_paths


    def set_pangenome_coordiantes(self):
        column_y_occupancy: Dict[int, List[int]] = {}
        for node_id, node in self.nodes_df.iterrows():
            if node.x_pangenome in column_y_occupancy:
                new_y = column_y_occupancy[node.x_pangenome][-1] + self.pangenome_space
                column_y_occupancy[node.x_pangenome].append(new_y)
            else:
                new_y = 0
                column_y_occupancy[node.x_pangenome] = [new_y]
            self.nodes_df.at[node_id, 'y_pangenome'] = new_y


    def set_poagraph_coordinates(self, jsonpangenome: PangenomeJSON):
        continuous_paths = self._find_continuous_paths()

        def find_out_y(continuous_path, cols_occupancy):
            columns_occupied_y = [cols_occupancy[jsonpangenome.nodes[node_id].column_id]
                                  for node_id in continuous_path]
            y_candidate = 0
            while True:
                if any([y_candidate == y and node_id not in continuous_path for co in columns_occupied_y for node_id, y in co.items()]):
                    # y_candidate += self.node_width * 1.5
                    y_candidate += self.poagraph_node_width * 1.5
                else:
                    for node_id in continuous_path:
                        cols_occupancy[jsonpangenome.nodes[node_id].column_id][node_id] = y_candidate
                    return y_candidate

        cols_occupancy: Dict[int, Dict[int, int]] = {col_id: {} for col_id in self.nodes_df['x_pangenome']}
        for sequence in jsonpangenome.sequences:
            for path in sequence.nodes_ids:
                for i, node_id in enumerate(path):
                    # if self.nodes_df.at[node_id, 'x_poagraph'] == -1:
                    #     update_x(node_id, jsonpangenome.nodes[node_id].column_id * self.scale)
                    if self.nodes_df.at[node_id, 'y_poagraph'] == -1:
                        col = jsonpangenome.nodes[node_id].column_id
                        if len(cols_occupancy[col]) == 0:
                            new_y_2 = 0
                        else:
                            new_y_2 = max([y for y in cols_occupancy[col].values()]) + self.poagraph_node_width * 1.5
                        cols_occupancy[col][node_id] = new_y_2
                        self.nodes_df.at[node_id, 'y_poagraph'] = new_y_2

        for continuous_path in continuous_paths:
            first_node_x = self.nodes_df.at[continuous_path[0], 'x_poagraph']
            last_node_id = self.nodes_df.at[continuous_path[-1], 'x_poagraph']

            middle_point = first_node_x + (last_node_id - first_node_x) / 2
            new_first_node_x = middle_point - len(continuous_path) // 2 * self.poagraph_node_width + self.poagraph_node_width / 2
            node_x = new_first_node_x
            path_y = find_out_y(continuous_path, cols_occupancy)
            for node_id in continuous_path:
                self.nodes_df.at[node_id, 'x_poagraph'] = node_x
                self.nodes_df.at[node_id, 'y_poagraph'] = path_y
                node_x += self.poagraph_node_width


def get_data(jsonpangenome: PangenomeJSON) -> Tuple[str, str]:
    if not jsonpangenome.sequences:
        return "", ""

    poagraph = PoaGraph(jsonpangenome)

    poagraph.set_pangenome_coordiantes()
    poagraph.set_poagraph_coordinates(jsonpangenome)

    edges_data = {'e1': ['n1', 'n3', [0, 1], []],
                  'e2': ['n2', 'n3', [2], [0, 1]]}
    df_edges = pd.DataFrame.from_dict(edges_data,
                                orient='index',
                                columns=['from', 'to', 'sequences_ids', 'consensuses_ids'])
    return poagraph.nodes_df.to_json(), df_edges.to_json()


def _get_cytoscape_node(id, label, x, y, cl):
    return {'data': {'id': id, 'label': f"{label}"}, 'position': {'x': x, 'y': y}, 'classes': cl}


def _get_cytoscape_edge(id, source, target, weight, cl):
    return {'data': {'source': source, 'target': target, 'weight': weight}, 'classes': cl}


def get_poagraph_elements(nodes_data, min_x: Optional[int], max_x: Optional[int]) -> List[any]:
    if max_x is None or min_x is None:
        r = _get_pangenome_graph_x_range(nodes_data)
        left_bound = r[1] // 3
        right_bound = r[1] // 3 * 2
    else:
        visible_axis_length = abs(max_x - min_x)
        left_bound = min_x + visible_axis_length // 3
        right_bound = min_x + visible_axis_length // 3 * 2

    nodes_to_display = nodes_data.loc[(nodes_data["x_pangenome"] >= left_bound)
                                      & (nodes_data["x_pangenome"] <= right_bound)]
    nodes = [_get_cytoscape_node(id=node_id,
                                 label=node_data['base'],
                                 x=node_data['x_poagraph'],
                                 y=node_data['y_poagraph'],
                                 cl='s_node')
             for node_id, node_data in nodes_to_display.iterrows()]
    edges = []
    for node_id, node in nodes_to_display.iterrows():
        for target in set(node['to_right']):
            e = _get_cytoscape_edge(id=len(edges),
                                    source=node_id,
                                    target=target,
                                    weight=len(node['sequences_ids'])/10,
                                    cl='s_edge')
            edges.append(e)
    return nodes + edges


def get_cytoscape_graph_old(nodes_data, edges_data) -> List[any]: #tu zwracam elements z cytoscape
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


def _get_pangenome_graph_x_range(nodes_data: pd.DataFrame) -> List[int]:
    max_x = nodes_data['x_pangenome'].max()
    return [-2, min(max_x + 2, 1000)]


def get_pangenome_figure(nodes_data: pd.DataFrame) -> go.Figure:
    if nodes_data.empty:
        return None

    pangenome_trace = _get_pangenome_graph(nodes_data)

    x_range = _get_pangenome_graph_x_range(nodes_data)
    y_range = [-3, 10]
    return go.Figure(
        data=[pangenome_trace],
        layout=go.Layout(
            dragmode='pan',
            yaxis=dict(
                range=y_range,
                fixedrange=True,
                showgrid=False,
                zeroline=False,
                showline=False,
                showticklabels=False
            ),
            xaxis=dict(
                range=x_range,
                showgrid=False,
                zeroline=False,
                showline=False,
                title="Drag the chart to the right or left to see details of the highlighted pangenome region."
            ),
            shapes=[
                {
                    'type': 'rect',
                    'xref': 'paper',
                    'yref': 'paper',
                    'x0': 0.3,
                    'y0': 0,
                    'x1': 0.6,
                    'y1': 1,
                    'line': {
                        'color': colors["dark_background"],
                        'width': 3,
                    }
                }
            ]
        )
    )


def _get_pangenome_graph(nodes_data) -> go.Scattergl:
    max_x = nodes_data['x_pangenome'].max()
    weights = [*map(lambda x: len(x), nodes_data['sequences_ids'])]
    desired_max = 10. if max_x/10 < 50 else 5.
    f = 2.*max(weights) / (desired_max ** 2)
    return go.Scattergl(
        x=nodes_data['x_pangenome'],
        y=nodes_data['y_pangenome']*(-1),
        hoverinfo='skip',
        mode='markers',
        marker=dict(
            size=weights,
            sizeref=f,
            sizemode='area',
            color=colors["light_accent"]
        ),
        name="Pangenome"
    )
