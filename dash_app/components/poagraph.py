import pickle

from ..components import tools
from flask import Flask, session
from ..layout.colors import colors
import colorsys
from typing import List, Dict, Tuple, Set, Optional, Any, Union

import math
import pandas as pd
from pangtreebuild.output.PangenomeJSON import PangenomeJSON, Sequence
import plotly.graph_objs as go

CytoscapeNode = Dict[str, Union[str, Dict[str, Any]]]
CytoscapeEdge = Dict[str, Union[str, Dict[str, Any]]]


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
                'width': '10'
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
                             'label': f"{label}",
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
    with open(user_session_elements_id, 'wb') as o:
        pickle.dump(d, o)


def get_poagraph_elements_faster(elements_cache_info, relayout_data):
    with open(elements_cache_info, 'rb') as i:
        poagraph_elements = pickle.load(i)
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
    c_to_n = poagraph_elements["cw"]
    nodes_ids_to_display = [n for nodes_ids in c_to_n[min_x:max_x+1] for n in nodes_ids]
    if nodes_ids_to_display:
        nodes = poagraph_elements["sn"][min(nodes_ids_to_display): max(nodes_ids_to_display)+1]
        edges = [e for src in nodes_ids_to_display for e in poagraph_elements["e"][src]]
    else:
        nodes = []
        edges = []
    return nodes + edges
