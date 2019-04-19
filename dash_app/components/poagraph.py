from collections import namedtuple, deque
from typing import List, Dict, Union, Tuple, Set
import pandas as pd
from poapangenome.output.PangenomeJSON import PangenomeJSON


EdgeData = namedtuple('EdgeData', ['to', 'classes'])

NodeData = namedtuple('NodeData', ['base', 'x_1', 'y_1', 'x_2', 'y_2', 'sequences_ids', 'consensus_ids'])

class Poagraph:
    def __init__(self):
        self.nodes: Dict[int, NodeData] = {}
        self.edges: Dict[int, EdgeData] = {}
        self.edges_reversed: Dict[int, Set[int]] = {}
        self.columns: Dict[int, Set[int]] = {}
        self.node_width: int = 10
        self.continuous_paths: List[List[int]] = []

    def update_coordinates_1(self):
        self.continuous_paths = self._get_continuous_paths()
        self._update_x_1_for_continuous_paths(self.continuous_paths)
        self._update_y_1()

    def _get_continuous_paths(self):
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

    def _update_x_1_for_continuous_paths(self, continuous_paths):
        for continuous_path in continuous_paths:
            first_node_x = self.nodes[continuous_path[0]].x_1
            last_node_id = self.nodes[continuous_path[-1]].x_1
            middle_point = first_node_x + (last_node_id - first_node_x) / 2
            new_first_node_x = middle_point - len(continuous_path) // 2 * self.node_width + self.node_width / 2
            node_x = new_first_node_x
            for node_id in continuous_path:
                n = self.nodes[node_id]
                self.nodes[node_id] = NodeData(n.base, node_x, n.y_1, n.x_2, n.y_2, n.sequences_ids, n.consensus_ids)
                node_x += self.node_width

    def _update_y_1(self):
        def update_next_node_y(next_nodes, i, new_y):
            n = self.nodes[next_nodes[i]]
            if n.y_1 == -1:
                self.nodes[next_nodes[i]] = NodeData(n.base, n.x_1, new_y, n.x_2, n.y_2, n.sequences_ids, n.consensus_ids)

        sorted_columns_ids = sorted(self.columns.keys())
        for column_id in sorted_columns_ids:
            nodes_ids = self.columns[column_id]
            current_y = 0
            column_y_values = []
            for node_id in nodes_ids:
                node = self.nodes[node_id]
                if node.y_1 != -1:
                    new_y = node.y_1
                else:
                    while True:
                        current_y += 20
                        if current_y not in column_y_values:
                            new_y = current_y
                            column_y_values.append(current_y)
                            break
                    self.nodes[node_id] = NodeData(node.base, node.x_1, new_y, node.x_2, node.y_2, node.sequences_ids, node.consensus_ids)
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

    def update_coordinates_2(self, jsonpangenome):
        def update_y_2(node_id, value):
            n = self.nodes[node_id]
            self.nodes[node_id] = NodeData(base=n.base,
                                           x_1=n.x_1, y_1=n.y_1,
                                           x_2=n.x_2, y_2=value,
                                           sequences_ids=n.sequences_ids,
                                           consensus_ids=n.consensus_ids)

        def update_x_2(node_id, value):
            n = self.nodes[node_id]
            self.nodes[node_id] = NodeData(base=n.base,
                                           x_1=n.x_1, y_1=n.y_1,
                                           x_2=value, y_2=n.y_2,
                                           sequences_ids=n.sequences_ids,
                                           consensus_ids=n.consensus_ids)

        def find_out_y(continuous_path, cols_occupancy):
            columns_occupied_y = [cols_occupancy[jsonpangenome.nodes[node_id].column_id] for node_id in continuous_path]
            y_candidate = 0
            while True:
                if any([y_candidate == y and node_id not in continuous_path for co in columns_occupied_y for node_id, y in co.items()]):
                    y_candidate += self.node_width * 1.5
                else:
                    for node_id in continuous_path:
                        cols_occupancy[jsonpangenome.nodes[node_id].column_id][node_id] = y_candidate
                    return y_candidate


        cols_occupancy: Dict[int, Dict[int, int]] = {col_id: {} for col_id in self.columns}
        for sequence in jsonpangenome.sequences:
            for path in sequence.nodes_ids:
                for i, node_id in enumerate(path):
                    if self.nodes[node_id].x_2 == -1:
                        update_x_2(node_id, jsonpangenome.nodes[node_id].column_id * self.node_width * 1.5)
                    if self.nodes[node_id].y_2 == -1:
                        col = jsonpangenome.nodes[node_id].column_id
                        if len(cols_occupancy[col]) == 0:
                            new_y_2 = 0
                        else:
                            new_y_2 = max([y for y in cols_occupancy[col].values()]) + self.node_width * 1.5
                        cols_occupancy[col][node_id] = new_y_2
                        update_y_2(node_id, new_y_2)

        for continuous_path in self.continuous_paths:
            first_node_x = self.nodes[continuous_path[0]].x_2
            last_node_id = self.nodes[continuous_path[-1]].x_2

            middle_point = first_node_x + (last_node_id - first_node_x) / 2
            new_first_node_x = middle_point - len(continuous_path) // 2 * self.node_width + self.node_width / 2
            node_x = new_first_node_x
            path_y = find_out_y(continuous_path, cols_occupancy)
            for node_id in continuous_path:
                n = self.nodes[node_id]
                self.nodes[node_id] = NodeData(n.base, n.x_1, n.y_1, node_x, path_y, n.sequences_ids, n.consensus_ids)
                node_x += self.node_width


def get_initial_poagraph(jsonpangenome: PangenomeJSON) -> Poagraph:
    poagraph = Poagraph()
    edges, edges_reversed, nodes, columns = {}, {}, {}, {}
    for sequence in jsonpangenome.sequences:
        for path in sequence.nodes_ids:
            for i, node_id in enumerate(path):
                node = jsonpangenome.nodes[node_id]
                if node.column_id in columns:
                    columns[node.column_id].add(node_id)
                else:
                    columns[node.column_id] = {node_id}

                if node_id in nodes:
                    nodes[node_id].sequences_ids.append(sequence.sequence_int_id)
                else:
                    node = jsonpangenome.nodes[node_id]
                    nodes[node_id] = NodeData(base=node.base,
                                              x_1=node.column_id * 25,
                                              y_1=-1,
                                              x_2=-1,
                                              y_2=-1,
                                              sequences_ids=[sequence.sequence_int_id],
                                              consensus_ids=[])
                if i < len(path) - 1:
                    left_end = node_id
                    right_end = path[i + 1]
                    if left_end in edges:
                        edges[left_end].to.append(right_end)
                    else:
                        edges[left_end] = EdgeData(to=[right_end], classes=[])
                    if right_end in edges_reversed:
                        edges_reversed[right_end].add(left_end)
                    else:
                        edges_reversed[right_end] = {left_end}
    poagraph.edges = edges
    poagraph.nodes = nodes
    poagraph.edges_reversed = edges_reversed
    poagraph.columns = columns
    return poagraph


def get_data(jsonpangenome: PangenomeJSON) -> Tuple[str, str]:
    if not jsonpangenome.sequences:
        return "", ""

    poagraph = get_initial_poagraph(jsonpangenome)
    poagraph.update_coordinates_1()
    poagraph.update_coordinates_2(jsonpangenome)

    df_nodes = pd.DataFrame.from_dict(poagraph.nodes,
                                      orient='index',
                                      columns=['base',
                                               'x_1',
                                               'y_1',
                                               'x_2',
                                               'y_2',
                                               'sequences_ids',
                                               'consensuses_ids'])

    edges_data = {'e1': ['n1', 'n3', [0, 1], []],
                  'e2': ['n2', 'n3', [2], [0, 1]]}
    df_edges = pd.DataFrame.from_dict(edges_data,
                                orient='index',
                                columns=['from', 'to', 'sequences_ids', 'consensuses_ids'])
    return df_nodes.to_json(), df_edges.to_json()


def get_node(id, label, x, y, cl):
    return {'data': {'id': id, 'label': f"{label} {id}"}, 'position': {'x': x, 'y': y}, 'classes': cl}


def get_cytoscape_graph(nodes_data, edges_data) -> List[any]: #tu zwracam elements z cytoscape
    nodes = [get_node(id=node_id,
                      label=node_data['base'],
                      x=node_data['x_2'],
                      y=node_data['y_2'],
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

