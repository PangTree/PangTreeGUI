from typing import Dict, Union, Any, Tuple, List

from pangtreebuild.serialization.json import PangenomeJSON
from dash_app.layout.colors import colors

CytoscapeNode = Dict[str, Union[str, Dict[str, Any]]]
CytoscapeEdge = Dict[str, Union[str, Dict[str, Any]]]


def get_mafgraph_stylesheet():
    return [
        {
            'selector': '.maf_node',
            'style': {
                'background-color': colors['light_background'],
                'border-color': colors['dark_background'],
                'border-width': '0.5px',
                'content': 'data(label)',
                # 'height': '10px',
                # 'width': '10px',
                'text-halign': 'center',
                'text-valign': 'center',
                'font-size': '5px',
                'opacity': 0.5
            }
        },
        {
            'selector': 'edge',
            'style': {

            }
        },
        {
            'selector': '.correct_edge',
            'style': {
                'width': 'data(weight)',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 0.5,
                'curve-style': 'bezier'
            }
        },
        {
            'selector': '.incorrect_edge',
            'style': {
                'width': 'data(weight)',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 0.5,
                'curve-style': 'bezier',
                'line-style': 'dashed'
            }
        }
    ]


def get_graph_elements(jsonpangenome: PangenomeJSON) -> Tuple[List[CytoscapeNode], List[CytoscapeEdge]]:
    def get_cytoscape_node(id, label, classes) -> CytoscapeNode:
        return {'data': {'id': id, 'label': label}, "classes": classes}

    def get_cytoscape_edge(source, target, weight, classes) -> CytoscapeEdge:
        return {'data': {'source': source, 'target': target, 'weight': weight}, "classes": classes}

    if not jsonpangenome.dagmaf_nodes:
        return [], []
    nodes = []
    edges = []
    for maf_node in jsonpangenome.dagmaf_nodes:

        nodes.append(get_cytoscape_node(str(maf_node.node_id),
                                        label=str(maf_node.node_id),
                                        classes="maf_node" + (" reversed" if maf_node.orient == -1 else "")))
        for edge in maf_node.out_edges:
            edges.append(get_cytoscape_edge(source=str(maf_node.node_id),
                                            target=str(edge.to_block),
                                            weight=len(edge.sequences),
                                            classes="correct_edge" if edge.edge_type == [1, -1] else "incorrect_edge"))

    return nodes, edges