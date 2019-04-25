from collections import namedtuple
from typing import List, Dict, Tuple, Set
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
        # self.detailed_node_width: int = 10
        self.pangenome_space = 1

        self.nodes_df = pd.DataFrame.from_records([{
            'id': node.id,
            'base': node.base,
            'x_detailed': -1,
            'y_detailed': -1,
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

        # for sequence in jsonpangenome.sequences:
        #     for path in sequence.nodes_ids:
        #         for i, node_id in enumerate(path):
        #             node = jsonpangenome.nodes[node_id]
        #             if node.column_id in self.columns:
        #                 self.columns[node.column_id].add(node_id)
        #             else:
        #                 self.columns[node.column_id] = {node_id}
        #
        #             if node_id in self.nodes:
        #                 self.nodes[node_id].sequences_ids.append(sequence.sequence_int_id)
        #             else:
        #                 node = jsonpangenome.nodes[node_id]
        #                 self.nodes[node_id] = NodeData(base=node.base,
        #                                                x_detailed=node.column_id * self.detailed_node_width * 1.5,
        #                                                y_detailed=-1,
        #                                                x_pangenome=node.column_id,
        #                                                y_pangenome=-1,
        #                                                sequences_ids=[sequence.sequence_int_id],
        #                                                consensus_ids=[]
        #                                                )
        #             if i < len(path) - 1:
        #                 left_end = node_id
        #                 right_end = path[i + 1]
        #                 if left_end in self.edges:
        #                     self.edges[left_end].to.append(right_end)
        #                 else:
        #                     self.edges[left_end] = EdgeData(to=[right_end], classes=[])
        #                 if right_end in self.edges_reversed:
        #                     self.edges_reversed[right_end].add(left_end)
        #                 else:
        #                     self.edges_reversed[right_end] = {left_end}

    def calculate_poagraph_coordinates(self):
        self.continuous_paths = self._find_continuous_paths()
        self._update_x_detailed_for_contlocinuous_paths(self.continuous_paths)
        self._update_y_detailed()

    def _find_continuous_paths(self) -> List[List[int]]:
        continuous_paths = []
        for node_id, node_data in self.nodes.items():
            if node_id not in self.edges:
                continue
            following_nodes_ids = list(set(self.edges[node_id].to))
            if len(following_nodes_ids) != 1:
                continue
            single_following_node_id = following_nodes_ids[0]
            other_incoming_nodes = list(set(self.edges_reversed[single_following_node_id]))
            if len(other_incoming_nodes) != 1:
                continue
            self.edges[node_id].classes.append("s_short")
            path_was_extended = False

            for continuous_path in continuous_paths:
                if continuous_path[-1] == node_id:
                    continuous_path.append(single_following_node_id)
                    path_was_extended = True
                    break
            if not path_was_extended:
                continuous_paths.append([node_id, single_following_node_id])
        return continuous_paths

    def _update_x_detailed_for_continuous_paths(self, continuous_paths):
        for continuous_path in continuous_paths:
            first_node_x = self.nodes[continuous_path[0]].x_detailed
            last_node_id = self.nodes[continuous_path[-1]].x_detailed
            middle_point = first_node_x + (last_node_id - first_node_x) / 2
            new_first_node_x = middle_point - len(continuous_path) // 2 * self.detailed_node_width + self.detailed_node_width / 2
            node_x = new_first_node_x
            for node_id in continuous_path:
                n = self.nodes[node_id]
                self.nodes[node_id] = NodeData(n.base, node_x, n.y_detailed, n.x_2, n.y_2, n.sequences_ids, n.consensus_ids)
                node_x += self.detailed_node_width

    def _update_y_detailed(self):
        def update_next_node_y(next_nodes, i, new_y):
            n = self.nodes[next_nodes[i]]
            if n.y_detailed == -1:
                self.nodes[next_nodes[i]] = NodeData(n.base, n.x_detailed, new_y, n.x_2, n.y_2, n.sequences_ids, n.consensus_ids)

        sorted_columns_ids = sorted(self.columns.keys())
        for column_id in sorted_columns_ids:
            nodes_ids = self.columns[column_id]
            current_y = 0
            column_y_values = []
            for node_id in nodes_ids:
                node = self.nodes[node_id]
                if node.y_detailed != -1:
                    new_y = node.y_detailed
                else:
                    while True:
                        current_y += 20
                        if current_y not in column_y_values:
                            new_y = current_y
                            column_y_values.append(current_y)
                            break
                    self.nodes[node_id] = NodeData(node.base, node.x_detailed, new_y, node.x_2, node.y_2, node.sequences_ids, node.consensus_ids)
                if node_id in self.edges:
                    next_nodes = [node_id for node_id in set(self.edges[node_id].to) if
                                  column_id < len(self.columns) - 1 and node_id in self.columns[column_id + 1]]
                    if len(next_nodes) == 1:
                        update_next_node_y(next_nodes, 0, new_y)
                    elif len(next_nodes) == 2:
                        update_next_node_y(next_nodes, 0, new_y - 10)
                        update_next_node_y(next_nodes, 1, new_y + 10)
                    elif len(next_nodes) == 3:
                        update_next_node_y(next_nodes, 0, new_y - 10)
                        update_next_node_y(next_nodes, 1, new_y)
                        update_next_node_y(next_nodes, 2, new_y + 10)
                    elif len(next_nodes) == 4:
                        update_next_node_y(next_nodes, 0, new_y - 25)
                        update_next_node_y(next_nodes, 1, new_y - 10)
                        update_next_node_y(next_nodes, 2, new_y + 10)
                        update_next_node_y(next_nodes, 3, new_y - 25)

    def calculate_pangenome_coordinates(self, jsonpangenome):
        def update_y(node_id, value):
            n = self.nodes[node_id]
            self.nodes[node_id] = NodeData(base=n.base,
                                           x_detailed=n.x_detailed, y_detailed=n.y_detailed,
                                           x_pangenome=n.x_2, y_pangenome=value,
                                           sequences_ids=n.sequences_ids,
                                           consensus_ids=n.consensus_ids)

        def update_x(node_id, value):
            n = self.nodes[node_id]
            self.nodes[node_id] = NodeData(base=n.base,
                                           x_detailed=n.x_detailed, y_detailed=n.y_detailed,
                                           x_pangenome=value, y_pangenome=n.y_2,
                                           sequences_ids=n.sequences_ids,
                                           consensus_ids=n.consensus_ids)

        def find_out_y(continuous_path, cols_occupancy):
            columns_occupied_y = [cols_occupancy[jsonpangenome.nodes[node_id].column_id] for node_id in continuous_path]
            y_candidate = 0
            while True:
                if any([y_candidate == y and node_id not in continuous_path for co in columns_occupied_y for node_id, y in co.items()]):
                    # y_candidate += self.node_width * 1.5
                    y_candidate += self.detailed_node_width
                else:
                    for node_id in continuous_path:
                        cols_occupancy[jsonpangenome.nodes[node_id].column_id][node_id] = y_candidate
                    return y_candidate

        cols_occupancy: Dict[int, Dict[int, int]] = {col_id: {} for col_id in self.columns}
        for sequence in jsonpangenome.sequences:
            for path in sequence.nodes_ids:
                for i, node_id in enumerate(path):
                    if self.nodes[node_id].x_2 == -1:
                        update_x(node_id, jsonpangenome.nodes[node_id].column_id * self.scale)
                    if self.nodes[node_id].y_2 == -1:
                        col = jsonpangenome.nodes[node_id].column_id
                        if len(cols_occupancy[col]) == 0:
                            new_y_2 = 0
                        else:
                            new_y_2 = max([y for y in cols_occupancy[col].values()]) + self.scale *2
                        cols_occupancy[col][node_id] = new_y_2
                        update_y(node_id, new_y_2)

        for continuous_path in self.continuous_paths:
            first_node_x = self.nodes[continuous_path[0]].x_2
            last_node_id = self.nodes[continuous_path[-1]].x_2

            middle_point = first_node_x + (last_node_id - first_node_x) / 2
            new_first_node_x = middle_point - len(continuous_path) // 2 * self.detailed_node_width + self.detailed_node_width / 2
            node_x = new_first_node_x
            path_y = find_out_y(continuous_path, cols_occupancy)
            for node_id in continuous_path:
                update_x(node_id, node_x)
                n = self.nodes[node_id]
                self.nodes[node_id] = NodeData(n.base, n.x_detailed, n.y_detailed, node_x, path_y, n.sequences_ids, n.consensus_ids)
                node_x += self.detailed_node_width

    def set_pangenome_coordiantes(self):
        def update_next_node_y(next_nodes, i, new_y):
            self.nodes_df.at[next_nodes[i], "y_pangenome"] = new_y
            # n = self.nodes[next_nodes[i]]
            # if n.y_detailed == -1:
            #     self.nodes[next_nodes[i]] = NodeData(n.base, n.x_detailed, n.y_detailed, n.x_pangenome, new_y, n.sequences_ids, n.consensus_ids)

        # sorted_columns_ids = sorted(set(self.nodes_df['x_pangenome']))
        # max_column_id = sorted_columns_ids[-1]
        column_y_occupancy: Dict[int, List[int]] = {}
        for node_id, node in self.nodes_df.iterrows():
            if node.x_pangenome in column_y_occupancy:
                new_y = column_y_occupancy[node.x_pangenome][-1] + self.pangenome_space
                column_y_occupancy[node.x_pangenome].append(new_y)
            else:
                new_y = 0
                column_y_occupancy[node.x_pangenome] = [new_y]
            self.nodes_df.at[node_id, 'y_pangenome'] = new_y

        # for column_id in sorted_columns_ids:
        #     nodes = self.nodes_df.loc[self.nodes_df['x_pangenome'] == column_id]
        #     current_y = 0
        #     column_y_values = []
            # for node_id, node in nodes.iterrows():
                # node = self.nodes_df.at[node_id]
                # if node.y_pangenome != -1:
                #     new_y = node.y_pangenome
                # else:
                #     while True:
                #         current_y += self.pangenome_space
                #         if current_y not in column_y_values:
                #             new_y = current_y
                #             column_y_values.append(current_y)
                #             break
                #     self.nodes_df.at[node_id, 'y_pangenome'] = new_y
                # if node_id in self.edges:
                # outgoing_nodes_ids = set(self.nodes_df.at[node_id, 'to_right'])
                # if len(outgoing_nodes_ids) > 0:#node_id in self.nodes_df.loc[]:   df.loc[node_id in df['to_right'].isin(some_values)]
                #     next_nodes = [node_id for node_id in set(outgoing_nodes_ids) if
                #                   # node.x_pangenome < max_column_id and
                #                   self.nodes_df.at[node_id, "x_pangenome"] == node.x_pangenome + 1]
                #     # next_nodes = [node_id for node_id in set(self.edges[node_id].to) if
                #     #               column_id < len(self.columns) - 1 and node_id in self.columns[column_id + 1]]
                #     if len(next_nodes) == 1:
                #         update_next_node_y(next_nodes, 0, new_y)
                #     elif len(next_nodes) == 2:
                #         update_next_node_y(next_nodes, 0, new_y - self.pangenome_space)
                #         update_next_node_y(next_nodes, 1, new_y + self.pangenome_space)
                #     elif len(next_nodes) == 3:
                #         update_next_node_y(next_nodes, 0, new_y - self.pangenome_space)
                #         update_next_node_y(next_nodes, 1, new_y)
                #         update_next_node_y(next_nodes, 2, new_y + self.pangenome_space)
                #     elif len(next_nodes) == 4:
                #         update_next_node_y(next_nodes, 0, new_y - 2*self.pangenome_space)
                #         update_next_node_y(next_nodes, 1, new_y - self.pangenome_space)
                #         update_next_node_y(next_nodes, 2, new_y + self.pangenome_space)
                #         update_next_node_y(next_nodes, 3, new_y + 2*self.pangenome_space)
        print("pangenome done")

def get_data(jsonpangenome: PangenomeJSON) -> Tuple[str, str]:
    if not jsonpangenome.sequences:
        return "", ""

    poagraph = PoaGraph(jsonpangenome)
    # poagraph.calculate_poagraph_coordinates()
    # poagraph.calculate_pangenome_coordinates(jsonpangenome)

    poagraph.set_pangenome_coordiantes()

    # df_nodes = pd.DataFrame.from_dict(poagraph.nodes,
    #                                   orient='index',
    #                                   columns=['base',
    #                                            'x_detailed',
    #                                            'y_detailed',
    #                                            'x_pangenome',
    #                                            'y_pangenome',
    #                                            'sequences_ids',
    #                                            'consensuses_ids'])

    edges_data = {'e1': ['n1', 'n3', [0, 1], []],
                  'e2': ['n2', 'n3', [2], [0, 1]]}
    df_edges = pd.DataFrame.from_dict(edges_data,
                                orient='index',
                                columns=['from', 'to', 'sequences_ids', 'consensuses_ids'])
    return poagraph.nodes_df.to_json(), df_edges.to_json()


def get_node(id, label, x, y, cl):
    return {'data': {'id': id, 'label': f"{label} {id}"}, 'position': {'x': x, 'y': y}, 'classes': cl}


def get_cytoscape_graph(nodes_data, edges_data) -> List[any]: #tu zwracam elements z cytoscape
    nodes = [get_node(id=node_id,
                      label=node_data['base'],
                      x=node_data['x_detailed'],
                      y=node_data['y_detailed'],
                      cl='s_node') for node_id, node_data in nodes_data.iterrows()]
    return nodes


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


def get_pangenome_graph(nodes_data, edges_data, jsonpangenome) -> go.Figure:
    if len(jsonpangenome.sequences) == 0:
        return None
    pangenome_trace = _get_pangenome_graph(nodes_data)

    max_x = nodes_data['x_pangenome'].max()
    x_range=[-2, min(max_x+2, 1000)]
    y_range=[-3,10]
    return go.Figure(
        data=[pangenome_trace],
        layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
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
        y=nodes_data['y_pangenome'],
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
