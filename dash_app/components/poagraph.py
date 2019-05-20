import pickle

from ..components import tools
from flask import Flask, session
from ..layout.colors import colors
import colorsys
from typing import List, Dict, Tuple, Set, Optional, Any, Union

import math
import pandas as pd
from poapangenome.output.PangenomeJSON import PangenomeJSON, Sequence
import plotly.graph_objs as go

CytoscapeNode = Dict[str, Union[str, Dict[str, Any]]]
CytoscapeEdge = Dict[str, Union[str, Dict[str, Any]]]

# test = {}
#
# class PoaGraph:
#     poagraph_node_width: int = 10
#     pangenome_space: int = 1
#     pangenome_x_range: List[int] = None
#
#     def __init__(self, jsonpangenome: PangenomeJSON):
#         nodes_df_generation_start = time()
#         self.nodes_df = pd.DataFrame.from_records([{
#             'id': node.id,
#             'base': node.base,
#             'aligned_to': node.aligned_to,
#             'x_poagraph': node.column_id * PoaGraph.poagraph_node_width * 1.5,
#             'y_poagraph': -1,
#             'column_id': node.column_id,
#             'y_pangenome': -1,
#             'sequences_ids': [],
#             'consensus_ids': [],
#             'to_left':[],
#             'to_right':[]
#         } for node in jsonpangenome.nodes], index='id')
#         nodes_df_generation_end = time()
#         print("nodes_df_generation", str(nodes_df_generation_end-nodes_df_generation_start))
#
#         edges_sequences_info_start = time()
#         for sequence in jsonpangenome.sequences:
#             for path in sequence.nodes_ids:
#                 path_end = len(path) - 1
#
#                 self.nodes_df.at[0, 'to_right'].append(path[1])
#                 self.nodes_df.at[path[-2], 'to_left'].append(path[-1])
#                 for i in range(1, len(path)-1):
#                     node_id = path[i]
#                     self.nodes_df.at[node_id, 'sequences_ids'].append(sequence.sequence_int_id)
#                     # if i != 0:
#                     self.nodes_df.at[node_id, 'to_left'].append(path[i-1])
#                     # if i < path_end:
#                     self.nodes_df.at[node_id, 'to_right'].append(path[i+1])
#         edges_sequences_info_end = time()
#         print("edges_sequences_info", str(edges_sequences_info_end - edges_sequences_info_start))
#
#         column_cut_width_start = time()
#         # self.columns_to_cut_width = self._get_columns_cut_width()
#         self.columns_to_cut_width = self._get_columns_cut_width_faster(jsonpangenome)
#         column_cut_width_end = time()
#         print("column_cut_width", str(column_cut_width_end - column_cut_width_start))
#
#     def _get_columns_cut_width_faster(self, jsonpangenome):
#         col_ids = set([node.column_id for node in jsonpangenome.nodes])
#         columns_cut_widths = [set() for col_id in col_ids]
#
#         for sequence in jsonpangenome.sequences:
#             for path in sequence.nodes_ids:
#                 for i in range(len(path)-1):
#                     current = path[i]
#                     next = path[i+1]
#
#                     current_col = jsonpangenome.nodes[current].column_id
#                     next_col = jsonpangenome.nodes[next].column_id
#                     for k in range(next_col-1, current_col-1, -1):
#                         # col = jsonpangenome.nodes[k].column_id
#                         columns_cut_widths[k].add((current, next))
#         columns_cut_widths = map(lambda x: len(x), columns_cut_widths)
#         return {col_id: y for col_id, y in enumerate(columns_cut_widths)}
#
#
#     def _get_columns_cut_width(self):
#
#         columns_cut_widths = {}
#         edges_between_non_consecutive_columns = {}
#
#         for column_id in sorted(self.nodes_df.column_id.unique()):
#             column_nodes = self.nodes_df[self.nodes_df.column_id == column_id]
#             column_cut_value = 0
#             for k, v in edges_between_non_consecutive_columns.items():
#                 if k > column_id:
#                     column_cut_value += 1
#             for node_id, node in column_nodes.iterrows():
#                 for node_id_to_right in set(node['to_right']):
#                     column_cut_value += 1
#                     edge_end_column = self.nodes_df.at[node_id_to_right, 'column_id']
#                     if edge_end_column != column_id +1:
#                         if edge_end_column in edges_between_non_consecutive_columns:
#                             edges_between_non_consecutive_columns[edge_end_column] += 1
#                         else:
#                             edges_between_non_consecutive_columns[edge_end_column] = 1
#
#             columns_cut_widths[str(column_id)] = column_cut_value
#
#
#         return columns_cut_widths
#
#     def _find_continuous_paths(self) -> List[List[int]]:
#         continuous_paths = []
#
#         for node_id, node in self.nodes_df.iterrows():
#             following_nodes_ids = list(set(node.to_right))
#             if len(following_nodes_ids) != 1:
#                 continue
#             single_following_node_id = following_nodes_ids[0]
#             other_incoming_nodes = list(set(self.nodes_df.loc[single_following_node_id, 'to_left']))
#             if len(other_incoming_nodes) != 1:
#                 continue
#             # self.edges[node_id].classes.append("s_short")
#             path_was_extended = False
#
#             for continuous_path in continuous_paths:
#                 if continuous_path[-1] == node_id:
#                     continuous_path.append(single_following_node_id)
#                     path_was_extended = True
#                     break
#             if not path_was_extended:
#                 continuous_paths.append([node_id, single_following_node_id])
#
#         return continuous_paths
#
#     @staticmethod
#     def pangenome_x_to_poagraph_x(pangenome_x: int)  -> int:
#         return pangenome_x * PoaGraph.poagraph_node_width * 1.5
#
#     def set_pangenome_coordinates(self):
#         column_y_occupancy: Dict[int, List[int]] = {}
#         for node_id, node in self.nodes_df.iterrows():
#             if node.column_id in column_y_occupancy:
#                 new_y = column_y_occupancy[node.column_id][-1] + PoaGraph.pangenome_space
#                 column_y_occupancy[node.column_id].append(new_y)
#             else:
#                 new_y = 0
#                 column_y_occupancy[node.column_id] = [new_y]
#             self.nodes_df.at[node_id, 'y_pangenome'] = new_y
#
#     def set_poagraph_coordinates(self, jsonpangenome: PangenomeJSON):
#         find_cont_paths_start = time()
#         continuous_paths = self._find_continuous_paths()
#         find_cont_paths_end = time()
#         print("find_cont_paths", str(find_cont_paths_end - find_cont_paths_start))
#
#         def find_out_y(continuous_path, cols_occupancy):
#             columns_occupied_y = [cols_occupancy[jsonpangenome.nodes[node_id].column_id]
#                                   for node_id in continuous_path]
#             y_candidate = 0
#             while True:
#                 if any([y_candidate == y and node_id not in continuous_path for co in columns_occupied_y for node_id, y in co.items()]):
#                     y_candidate += PoaGraph.poagraph_node_width * 1.5
#                 else:
#                     for node_id in continuous_path:
#                         cols_occupancy[jsonpangenome.nodes[node_id].column_id][node_id] = y_candidate
#                     return y_candidate
#
#         part1_start = time()
#         cols_occupancy: Dict[int, Dict[int, int]] = {col_id: {} for col_id in self.nodes_df['column_id']}
#         for sequence in jsonpangenome.sequences:
#             for path in sequence.nodes_ids:
#                 for i, node_id in enumerate(path):
#                     # if self.nodes_df.at[node_id, 'x_poagraph'] == -1:
#                     #     update_x(node_id, jsonpangenome.nodes[node_id].column_id * self.scale)
#                     if self.nodes_df.at[node_id, 'y_poagraph'] == -1:
#                         col = jsonpangenome.nodes[node_id].column_id
#                         if len(cols_occupancy[col]) == 0:
#                             new_y_2 = 0
#                         else:
#                             new_y_2 = max([y for y in cols_occupancy[col].values()]) + PoaGraph.poagraph_node_width * 1.5
#                         cols_occupancy[col][node_id] = new_y_2
#                         self.nodes_df.at[node_id, 'y_poagraph'] = new_y_2
#         part1_end = time()
#         print("part1", str(part1_end - part1_start))
#
#         part2_start = time()
#         for continuous_path in continuous_paths:
#             first_node_x = self.nodes_df.at[continuous_path[0], 'x_poagraph']
#             last_node_id = self.nodes_df.at[continuous_path[-1], 'x_poagraph']
#
#             middle_point = first_node_x + (last_node_id - first_node_x) / 2
#             new_first_node_x = middle_point - 2/3*len(continuous_path) // 2 * PoaGraph.poagraph_node_width + PoaGraph.poagraph_node_width / 3
#             node_x = new_first_node_x
#             path_y = find_out_y(continuous_path, cols_occupancy)
#             for node_id in continuous_path:
#                 self.nodes_df.at[node_id, 'x_poagraph'] = node_x
#                 self.nodes_df.at[node_id, 'y_poagraph'] = path_y
#                 node_x += PoaGraph.poagraph_node_width * 2/3
#         part2_end = time()
#         print("part2", str(part2_end - part2_start))
#
#     def get_poagraph_elements(self, jsonpangenome: PangenomeJSON) -> Tuple[List[CytoscapeNode], List[CytoscapeEdge]]:
#         def _get_cytoscape_node(id, label, x, y, cl, sequences_ids, consensus_ids, column_id) -> CytoscapeNode:
#             return {'data': {'id': id,
#                              'label': f"{label}",
#                              'sequences_ids': sequences_ids,
#                              'consensus_ids': consensus_ids,
#                              'column_id': column_id},
#                     'position': {'x': x, 'y': y},
#                     'classes': cl}
#
#         def _get_cytoscape_edge(id, source, target, weight, cl) -> CytoscapeEdge:
#             return {'data': {'label': cl, 'source': source, 'target': target, 'weight': weight}, 'classes': cl}
#
#         nodes = [_get_cytoscape_node(id=node_id,
#                                      label=node_data['base'],
#                                      x=node_data['x_poagraph'],
#                                      y=node_data['y_poagraph'],
#                                      cl='s_node',
#                                      sequences_ids=node_data['sequences_ids'],
#                                      consensus_ids=node_data['consensus_ids'],
#                                      column_id=node_data['column_id'])
#                  for node_id, node_data in self.nodes_df.iterrows()] + \
#                 [_get_cytoscape_node(id=node_id,
#                                      label='',
#                                      x=node_data['x_poagraph'],
#                                      y=node_data['y_poagraph'],
#                                      cl='c_node',
#                                      sequences_ids=[],
#                                      consensus_ids=[],
#                                      column_id=node_data['column_id']
#                                      )
#                  for node_id, node_data in self.nodes_df.iterrows()]
#
#
#         edges = []
#         for node_id, node in self.nodes_df.iterrows():
#             for target in set(node['to_right']):
#                 e = _get_cytoscape_edge(id=len(edges),
#                                         source=node_id,
#                                         target=target,
#                                         weight=math.log10(len(node['sequences_ids'])+1),
#                                         cl='s_edge')
#                 edges.append(e)
#                 if self.nodes_df.at[target, 'column_id'] != self.nodes_df.at[node_id, 'column_id'] + 1:
#                     tricky_edge = _get_cytoscape_edge(id=len(edges),
#                                         source=node_id,
#                                         target=target,
#                                         weight=0,
#                                         cl='s_edge')
#                     edges.append(tricky_edge)
#         edges.extend([_get_cytoscape_edge(id='',
#                                       source=node_id,
#                                       target= node_data['aligned_to'],
#                                       weight=1,
#                                       cl='s_edge_aligned')
#                   for node_id, node_data in self.nodes_df.iterrows()])
#         # if jsonpangenome.consensuses:
#         #     for consensus in jsonpangenome.consensuses:
#         #         for i in range(len(consensus.nodes_ids)-1):
#         #             c_edge = _get_cytoscape_edge(id=len(edges),
#         #                                          source=consensus.nodes_ids[i],
#         #                                          target=consensus.nodes_ids[i+1],
#         #                                          weight=math.log10(len(consensus.sequences_int_ids)+1),
#         #                                          cl=f'c_edge c{consensus.name}')
#         #             edges.append(c_edge)
#
#         return nodes, edges


# def get_data(jsonpangenome: PangenomeJSON) -> Tuple[Dict[str, int], List[CytoscapeNode], List[CytoscapeEdge]]:
#     if not jsonpangenome.sequences:
#         return {}, [], []
#     all_start = time()
#     poagraph = PoaGraph(jsonpangenome)
#
#     # poagraph.set_pangenome_coordinates()
#     poagraph.set_poagraph_coordinates(jsonpangenome)
#
#     elem_start = time()
#     cytoscape_nodes, cytoscape_edges = poagraph.get_poagraph_elements(jsonpangenome)
#     elem_end = time()
#     print("elem", str(elem_end - elem_start))
#     all_end = time()
#     print("all", str(all_end - all_start))
#     return poagraph.columns_to_cut_width, cytoscape_nodes, cytoscape_edges
#
#
# def get_poagraph_elements(nodes: List[CytoscapeNode],
#                           edges: List[CytoscapeEdge],
#                           min_x: Optional[int],
#                           max_x: Optional[int]) -> List[any]:
#     update_start = time()
#
#     up_p1_start = time()
#     if max_x is None or min_x is None:
#         # if PoaGraph.pangenome_x_range is None:
#         #     raise Exception("Cannot draw poagraph.")
#         # r = PoaGraph.pangenome_x_range
#         r = _get_pangenome_graph_x_range([n['data']['column_id'] for n in nodes])
#         left_bound = PoaGraph.pangenome_x_to_poagraph_x(r[1] // 3)
#         right_bound = PoaGraph.pangenome_x_to_poagraph_x(r[1] // 3 * 2)
#     else:
#         visible_axis_length = abs(max_x - min_x)
#         left_bound = PoaGraph.pangenome_x_to_poagraph_x(min_x + visible_axis_length // 3)
#         right_bound = PoaGraph.pangenome_x_to_poagraph_x(min_x + visible_axis_length // 3 * 2)
#     up_p1_end = time()
#     print("up_1", str(up_p1_end - up_p1_start))
#
#     up_p1_start = time()
#     nodes = [node for node in nodes if node['position']['x'] >= left_bound and node['position']['x'] <= right_bound]
#     up_p1_end = time()
#     print("up_1", str(up_p1_end - up_p1_start))
#
#     up_p2_start = time()
#     nodes_ids = [node["data"]["id"] for node in nodes]
#     up_p2_end = time()
#     print("up_2", str(up_p2_end - up_p2_start))
#
#     up_p3_start = time()
#     # edges = [edge for edge in edges if edge['data']['source'] in nodes_ids and edge['data']['target'] in nodes_ids]
#     up_p3_end = time()
#     print("up_3", str(up_p3_end - up_p3_start))
#
#     update_end = time()
#     print("update", str(update_end - update_start))
#     return nodes + edges
#     # nodes_to_display = nodes_data.loc[(nodes_data["column_id"] >= left_bound)
#     #                                   & (nodes_data["column_id"] <= right_bound)]

#
# def get_cytoscape_graph_old(nodes_data, edges_data) -> List[any]: #tu zwracam elements z cytoscape
#     def get_node(id, label, x, y, cl, sequences_ids, consensuses_ids):
#         return {'data': {'id': id,
#                          'label': label,
#                          'sequences_ids': sequences_ids,
#                          'consensuses_ids': consensuses_ids},
#                 'position': {'x': x, 'y': y},
#                 'classes': cl}
#
#     def get_c_node(id, x, y, cl):
#         return {'data': {'id': id}, 'position': {'x': x, 'y': y}, 'classes': cl}
#
#     def get_edge(id, source, target, weight, cl):
#         return {'data': {'source': source, 'target': target, 'weight': weight}, 'classes': cl}
#         # return {'data': {'id': id, 'source': source, 'target': target, 'weight': weight}, 'classes': cl}
#
#     nodes = [get_node(i, l, x, y, c) for i, l, x, y, c in [('n1', 'C', 50, 50, 'C s_node'),
#                                                            ('n2', 'G', 50, 100, 'G s_node'),
#                                                            ('n3', 'G', 80, 75, 'G s_node'),
#                                                            ('n4', 'T', 90, 75, 'T s_node'),
#                                                            ('n5', 'A', 100, 75, 'A s_node'),
#                                                            ('n6', 'A', 130, 50, 'A s_node'),
#                                                            ('n7', 'G', 130, 75, 'G s_node'),
#                                                            ('n8', 'A', 130, 100, 'A s_node'),
#                                                            ('n9', 'A', 160, 50, 'A provided  s_node'),
#                                                            ('n10', 'T', 160, 75, 'T s_node'),
#                                                            ('n11', 'G', 170, 75, 'G s_node'),
#                                                            ('n12', 'A', 200, 75, 'A s_node')]]
#
#     c_nodes = [get_c_node(i, x, y, c) for i, x, y, c in [('cn1', 50, 50, 'c_node'),
#                                                          ('cn2', 50, 100, 'c_node'),
#                                                          ('cn3', 80, 75, 'c_node'),
#                                                          ('cn4', 90, 75, 'c_node'),
#                                                          ('cn5', 100, 75, 'c_node'),
#                                                          ('cn6', 130, 50, 'c_node'),
#                                                          ('cn7', 130, 75, 'c_node'),
#                                                          ('cn8', 130, 100, 'c_node'),
#                                                          ('cn9', 160, 50, 'c_node'),
#                                                          ('cn10', 160, 75, 'c_node'),
#                                                          ('cn11', 170, 75, 'c_node'),
#                                                          ('cn12', 200, 75, 'c_node')]]
#
#     edges = [get_edge(i, s, t, w, c) for i, s, t, w, c in [('e1', 'n1', 'n3', 2, 's_edge'),
#                                                            # ('e2', 'n2', 'n3', 1, 's_edge'),
#                                                            ('e3', 'n3', 'n4', 3, 's_edge'),
#                                                            ('e4', 'n4', 'n5', 3, 's_edge'),
#                                                            ('e5', 'n5', 'n6', 1, 's_edge'),
#                                                            ('e6', 'n5', 'n7', 1, 's_edge'),
#                                                            ('e7', 'n5', 'n8', 1, 's_edge'),
#                                                            ('e8', 'n6', 'n7', 1, 's_edge_aligned'),
#                                                            ('e9', 'n7', 'n8', 1, 's_edge_aligned'),
#                                                            ('e10', 'n6', 'n9', 1, 's_edge'),
#                                                            ('e11', 'n6', 'n10', 1, 's_edge'),
#                                                            ('e12', 'n7', 'n10', 1, 's_edge'),
#                                                            ('e13', 'n8', 'n12', 1, 's_edge'),
#                                                            ('e14', 'n9', 'n12', 1, 's_edge'),
#                                                            ('e15', 'n11', 'n12', 1, 's_edge'),
#
#                                                            ('e16', 'cn2', 'cn3', 2, 'c_edge c1'),
#                                                            ('e17', 'cn3', 'cn4', 2, 'c_edge c1 c_short'),
#                                                            ('e18', 'cn4', 'cn5', 2, 'c_edge c1 c_short'),
#                                                            ('e19', 'cn5', 'cn7', 2, 'c_edge c1'),
#                                                            ('e21', 'cn10', 'cn11', 2, 'c_edge c1'),
#                                                            ('e22', 'cn11', 'cn12', 2, 'c_edge c1'),
#                                                            ('e20', 'cn7', 'cn10', 2, 'c_edge c1'),
#
#                                                            ('e21', 'cn2', 'cn3', 2, 'c_edge c2'),
#                                                            ('e22', 'cn3', 'cn4', 2, 'c_edge c2 c_short'),
#                                                            ('e23', 'cn4', 'cn5', 2, 'c_edge c2 c_short'),
#                                                            ('e24', 'cn5', 'cn6', 2, 'c_edge c2'),
#                                                            ('e25', 'cn6', 'cn9', 2, 'c_edge c2'),
#                                                            ('e26', 'cn9', 'cn12', 2, 'c_edge c2'),
#
#                                                            ]]
#     return nodes + c_nodes + edges


# def _get_pangenome_graph_x_range(column_ids: List[int]) -> List[int]:
#     max_x = max(column_ids)
#     return [-2, min(max_x + 2, 2000)]

#
# def get_pangenome_figure(pangenome_graph_data: Dict[str, int]) -> go.Figure:
#     if len(pangenome_graph_data) == 0:
#         return None
#
#     pangenome_trace = _get_cut_width_graph(pangenome_graph_data)
#
#     PoaGraph.pangenome_x_range =_get_pangenome_graph_x_range(pangenome_trace.x)
#     max_y = max(pangenome_trace.y)
#     y_range = [0, max_y+1]
#     return go.Figure(
#         data=[pangenome_trace],
#         layout=go.Layout(
#             dragmode='pan',
#             yaxis=dict(
#                 range=y_range,
#                 fixedrange=True,
#                 tickvals=[i for i in range(max_y+1)]
#             ),
#             xaxis=dict(
#                 range=PoaGraph.pangenome_x_range,
#                 showgrid=False,
#                 zeroline=False,
#                 showline=False,
#                 title="Drag the chart to the right or left to see details of the highlighted pangenome region."
#             ),
#             shapes=[
#                 {
#                     'type': 'rect',
#                     'xref': 'paper',
#                     'yref': 'paper',
#                     'x0': 0.3,
#                     'y0': 0,
#                     'x1': 0.6,
#                     'y1': 1,
#                     'line': {
#                         'color': colors["dark_background"],
#                         'width': 1,
#                     }
#                 }
#             ]
#         )
#     )

#
# def _get_cut_width_graph(column_id_to_cut_width: Dict[str, int]) -> go.Scattergl:
#     [column_ids, cut_widths] = [*zip(*[(int(k), v) for k, v in column_id_to_cut_width.items()])]
#     return go.Scattergl(
#         x=column_ids,
#         y=cut_widths,
#         hoverinfo='skip',
#         mode='lines',
#         marker=dict(
#             color=colors["light_accent"]
#         ),
#         name="Pangenome Cut Width"
#     )

#
# def _get_pangenome_graph(nodes_df) -> go.Scattergl:
#     max_x = nodes_df['column_id'].max()
#     weights = [*map(lambda x: len(x), nodes_df['sequences_ids'])]
#     desired_max = 10. if max_x/10 < 50 else 5.
#     f = 2.*max(weights) / (desired_max ** 2)
#     return go.Scattergl(
#         x=nodes_df['column_id'],
#         y=nodes_df['y_pangenome'] * (-1),
#         hoverinfo='skip',
#         mode='markers',
#         marker=dict(
#             size=weights,
#             sizeref=f,
#             sizemode='area',
#             color=colors["light_accent"]
#         ),
#         name="Pangenome"
#     )


def HSVToRGB(h, s, v):
    (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
    return (int(255*r), int(255*g), int(255*b))


def get_distinct_colors(n):
    huePartition = 1.0 / (n + 1)
    return [HSVToRGB(huePartition * value, 1.0, 1.0) for value in range(0, n)]


def get_poagraph_stylesheet():
    return [
        {
            'selector': 'node',
            'style': {
                'background-color': 'white',
            }
        },
        {
            'selector': '.s_node',
            'style': {
                'background-color': colors['background'],
                # 'border-color': 'green',
                # 'border-width': '0.5px',
                'content': 'data(label)',
                'height': '10px',
                'width': '10px',
                'text-halign': 'center',
                'text-valign': 'center',
                'font-size': '5px',
                # 'shape': 'circle',
            }
        },
        {
            'selector': '.c_node',
            'style': {
                'height': '7px',
                'width': '7px',
                'opacity': 0.5
            }
        },
        {
            'selector': 'edge',
            'style': {

            }
        },
        {
            'selector': '.s_edge',
            'style': {
                'width': 'data(weight)',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 0.5,
                'curve-style': 'bezier'
            }
        },
        {
            'selector': '.c_edge',
            'style': {
                'opacity': 0.5,
                'curve-style': 'haystack',
                'haystack-radius': 0.3,
                'width': 'data(weight)',
                # 'label': 'data(label)'
            }
        },
        {
            'selector': '.c2',
            'style': {
                'line-color': 'red',
            }
        },
        {
            'selector': '.c1',
            'style': {
                'line-color': 'green',
            }
        },
        {
            'selector': '.c_short',
            'style': {
                'curve-style': 'haystack',
            }
        },
        {
            'selector': '.s_short',
            'style': {
                'curve-style': 'haystack',
            }
        },
        {
            'selector': '.s_edge_aligned',
            'style': {
                'line-style': 'dashed',
                'width': '0.5'
            }
        },
    ]


def _get_pangenome_graph_x_range_faster(max_column_id: int) -> Tuple:
    return (-2, min(max_column_id + 2, 2000))


def get_pangenome_figure_faster(jsonpangenome: PangenomeJSON) -> go.Figure:

    def get_columns_cut_width(jsonpangenome) -> List[int]:
        col_ids = set([node.column_id for node in jsonpangenome.nodes])
        columns_cut_widths = [set() for _ in col_ids]

        for sequence in jsonpangenome.sequences:
            for path in sequence.nodes_ids:
                for i in range(len(path)-1):
                    current = path[i]
                    next = path[i+1]

                    current_col = jsonpangenome.nodes[current].column_id
                    next_col = jsonpangenome.nodes[next].column_id
                    for k in range(next_col-1, current_col-1, -1):
                        columns_cut_widths[k].add((current, next))
        return [len(x) for x in columns_cut_widths]

    def get_cut_width_trace(columns_cut_width: List[int]) -> go.Scattergl:
        return go.Scattergl(
            x=[*range(len(columns_cut_width))],
            y=columns_cut_width,
            hoverinfo='skip',
            mode='lines',
            marker=dict(
                color=colors["accent"]
            ),
            name="Pangenome Cut Width"
        )

    columns_cut_width = get_columns_cut_width(jsonpangenome)
    pangenome_trace = get_cut_width_trace(columns_cut_width)

    pangenome_x_range = _get_pangenome_graph_x_range_faster(len(columns_cut_width)-1)
    max_y = max(columns_cut_width)
    y_range = [0, max_y + 1]
    return go.Figure(
        data=[pangenome_trace],
        layout=go.Layout(
            dragmode='pan',
            yaxis=dict(
                range=y_range,
                fixedrange=True,
                tickvals=[i for i in range(max_y + 1)]
            ),
            xaxis=dict(
                range=[pangenome_x_range[0], pangenome_x_range[1]],
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
                        'width': 1,
                    }
                }
            ]
        )
    )


def remove_elements_data_faster(elements_cache_info):
    pass
    # del test[elements_cache_info]
    # tools.remove_file(elements_cache_info)


def update_cached_poagraph_elements_faster(user_session_elements_id, jsonpangenome: PangenomeJSON):
    def get_y(column_id, node_id):
        if column_id not in cols_occupancy:
            cols_occupancy[column_id] = {node_id: 0}
            columns[column_id] = [node_id]
            return 0
        else:
            y = max([*cols_occupancy[column_id].values()]) + node_y_distance
            cols_occupancy[column_id][node_id] = y
            columns[column_id].append(node_id)
            return y

    def get_continuous_paths() -> List[List[int]]:
        continuous_paths: List[List[int]] = []
        for from_node_id, to_node_ids in edges.items():
            followers = list(set(to_node_ids))
            if len(followers) == 1 and len(set(edges_reverted[followers[0]])) == 1:
                path_was_extended = False

                for continuous_path in continuous_paths:
                    if continuous_path[-1] == from_node_id:
                        continuous_path.append(followers[0])
                        path_was_extended = True
                        break
                if not path_was_extended:
                    continuous_paths.append([from_node_id, followers[0]])
        return continuous_paths

    def find_out_y(continuous_path):
        columns_occupied_y = [cols_occupancy[jsonpangenome.nodes[node_id].column_id]
                              for node_id in continuous_path]
        y_candidate = 0
        while True:
            if any([y_candidate == y and node_id not in continuous_path for co in columns_occupied_y for node_id, y in
                    co.items()]):
                y_candidate += node_y_distance
            else:
                for node_id in continuous_path:
                    cols_occupancy[jsonpangenome.nodes[node_id].column_id][node_id] = y_candidate
                return y_candidate

    def get_cytoscape_node(id, label, x, y, cl, sequences_ids, consensus_ids) -> CytoscapeNode:
            return {'data': {'id': id,
                             'label': f"{label} {id}",
                             'sequences_ids': sequences_ids,
                             'consensus_ids': consensus_ids},
                    'position': {'x': x, 'y': y},
                    'classes': cl}

    def get_cytoscape_edge(source, target, weight, cl) -> CytoscapeEdge:
        return {'data': {'label': cl, 'source': source, 'target': target, 'weight': weight}, 'classes': cl}

    def get_poagraph_elements() -> Tuple[List[CytoscapeNode], Dict[int, List[CytoscapeEdge]]]:
        sequences_nodes = [get_cytoscape_node(id=node_id,
                                     label=node_info[3],
                                     x=node_info[0],
                                     y=node_info[1],
                                     cl='s_node',
                                     sequences_ids=nodes_to_sequences[node_id],
                                     consensus_ids=[])
                                     # consensus_ids=node_data['consensus_ids'])
                 for node_id, node_info in enumerate(nodes)]
        # consensuses_nodes = [get_cytoscape_node(id=node_id,
        #                                       label=node_info[3],
        #                                       x=node_info[0],
        #                                       y=node_info[1],
        #                                       cl='s_node',
        #                                       sequences_ids=nodes_to_sequences[node_id],
        #                                       consensus_ids=[])
        #                    # consensus_ids=node_data['consensus_ids'])
        #                    for node_id, node_info in enumerate(nodes)]
        all_edges = {}
        for src_node_id, targets in edges.items():
            targets_unique = set(targets)
            all_edges[src_node_id] = [get_cytoscape_edge(src_node_id,
                                                     t,
                                                     math.log10(targets.count(t)+1),
                                                     's_edge')
                                  for t in targets_unique]
            for t in targets_unique:
                if jsonpangenome.nodes[t].column_id != jsonpangenome.nodes[src_node_id].column_id + 1:
                    all_edges[src_node_id].append(get_cytoscape_edge(source=src_node_id,
                                                                 target=t,
                                                                 weight=0,
                                                                 cl='s_edge'))
        for i, node in enumerate(nodes):
            if node[3] != None:
                if i in all_edges:
                    all_edges[i].append(get_cytoscape_edge(
                                      source=i,
                                      target= node[3],
                                      weight=1,
                                      cl='s_edge_aligned'))
                else:
                    all_edges[i] = [get_cytoscape_edge(
                        source=i,
                        target=node[3],
                        weight=1,
                        cl='s_edge_aligned')]

        # if jsonpangenome.consensuses:
        #     for consensus in jsonpangenome.consensuses:
        #         for i in range(len(consensus.nodes_ids)-1):
        #             c_edge = get_cytoscape_edge(
        #                                          source=consensus.nodes_ids[i],
        #                                          target=consensus.nodes_ids[i+1],
        #                                          weight=math.log10(len(consensus.sequences_int_ids)+1),
        #                                          cl=f'c_edge c{consensus.name}')
        #             all_edges[consensus.nodes_ids[i]].append(c_edge)

        return sequences_nodes, all_edges

    nodes = [None] * len(jsonpangenome.nodes)  # id ~ (x, y, aligned_to)
    nodes_to_sequences = dict()  # id ~ [sequences_ids]
    cols_occupancy: Dict[int, Dict[int, int]] = dict()
    columns = [None] * (max([n.column_id for n in jsonpangenome.nodes])+1)  # column_id ~ [nodes_ids]
    edges = dict()  # node_id ~ [nodes_ids]
    edges_reverted = dict()  # node_id ~ [nodes_ids]
    node_width = 10
    node_y_distance = node_width * 1.5
    continuous_path_nodes_distance = node_width * 2/3

    for sequence in jsonpangenome.sequences:
        for path in sequence.nodes_ids:
            for i in range(len(path) - 1):
                current_node_id = path[i]
                current_node = jsonpangenome.nodes[current_node_id]
                next_node_id = path[i + 1]
                if current_node_id in nodes_to_sequences:
                    nodes_to_sequences[current_node_id].append(sequence.sequence_int_id)
                    if current_node_id in edges:
                        edges[current_node_id].append(next_node_id)
                    else:
                        edges[current_node_id] = [next_node_id]
                else:
                    nodes_to_sequences[current_node_id] = [sequence.sequence_int_id]
                    x = current_node.column_id * node_y_distance
                    col_id = current_node.column_id
                    y = get_y(col_id, current_node_id)
                    nodes[current_node_id] = (x, y, current_node.aligned_to, current_node.base, col_id)
                    edges[current_node_id] = [next_node_id]
                if next_node_id in edges_reverted:
                    edges_reverted[next_node_id].append(current_node_id)
                else:
                    edges_reverted[next_node_id] = [current_node_id]
            last_node_id = path[-1]
            last_node = jsonpangenome.nodes[last_node_id]
            if last_node_id in nodes_to_sequences:
                nodes_to_sequences[last_node_id].append(sequence.sequence_int_id)
            else:
                nodes_to_sequences[last_node_id] = [sequence.sequence_int_id]
                x = last_node.column_id * node_y_distance
                col_id = last_node.column_id
                y = get_y(col_id, last_node_id)
                nodes[last_node_id] = (x, y, current_node.aligned_to, current_node.base, col_id)

    continuous_paths = get_continuous_paths()

    for continuous_path in continuous_paths:
        first_node_x = nodes[continuous_path[0]][0]
        last_node_x = nodes[continuous_path[-1]][0]
        middle_point = first_node_x + (last_node_x - first_node_x) / 2
        new_first_node_x = middle_point - 2 / 3 * len(
            continuous_path) // 2 * node_width + node_width / 3
        node_x = new_first_node_x
        path_y = find_out_y(continuous_path)
        for node_id in continuous_path:
            nodes[node_id] = (node_x, path_y, nodes[node_id][2], nodes[node_id][3], nodes[node_id][4])
            node_x += continuous_path_nodes_distance

    sequences_nodes, edges = get_poagraph_elements()
    d = {"sn": sequences_nodes,
         "e": edges,
         "cw": columns}
    # test[user_session_elements_id] = d
    session[user_session_elements_id] = d
    # with open(user_session_elements_id, 'wb') as o:
    #     pickle.dump(d, o)


def get_poagraph_elements_faster(elements_cache_info, relayout_data):
    def recalc(x):
        return x //  15
    # with open(elements_cache_info, 'rb') as i:
    #     poagraph_elements = pickle.load(i)
    # poagraph_elements = test[elements_cache_info]
    poagraph_elements = session[elements_cache_info]
    max_column_id = len(poagraph_elements["cw"])+1
    try:
        min_x = int(relayout_data['xaxis.range[0]'])
        max_x = int(relayout_data['xaxis.range[1]'])
        visible_axis_length = abs(max_x - min_x)
        min_x = max(0, min_x + int(max_column_id *0.3))
        max_x = min(min_x + int(0.3 * max_column_id), max_column_id)#visible_axis_length // 3 * 2
    except KeyError:
        min_x = int(0.3*max_column_id)
        max_x = int(0.6*max_column_id)
        # r = _get_pangenome_graph_x_range([n['data']['column_id'] for n in nodes])
        #         left_bound = PoaGraph.pangenome_x_to_poagraph_x(r[1] // 3)
        #         right_bound = PoaGraph.pangenome_x_to_poagraph_x(r[1] // 3 * 2)
    min_x=0
    max_x=max_column_id
    # min_x = random.randint(0,5)
    # max_x = random.randint(5,10)
    c_to_n = poagraph_elements["cw"]
    nodes_ids_to_display = [n for nodes_ids in c_to_n[min_x:max_x+1] for n in nodes_ids]
    if nodes_ids_to_display:
        nodes = poagraph_elements["sn"][min(nodes_ids_to_display): max(nodes_ids_to_display)+1]
        edges = [e for src in nodes_ids_to_display for e in poagraph_elements["e"][src]]
    else:
        nodes = []
        edges = []
    return nodes + edges
#
