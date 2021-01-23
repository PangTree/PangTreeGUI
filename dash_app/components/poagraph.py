import copy
import json
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go

from dash_app.components import consensustable, consensustree, tools
from dash_app.server import app


class Node:
    def __init__(self, idx: int, base: str, column: int):
        self.id = idx
        self.base = base
        self.column = column
        
    def __repr__(self):
        return f"{self.base} ID: {self.id}, COLUMN: {self.column}"


class GraphAlignment:
    def __init__(self, data):
        self.column_dict = None
        self.consensus_sequence = None
        self.nodes = None
        self.sequences = None
        self.diagram = None
        app.callback(
            [Output("poagraph", "figure"),
             Output("selected_vertex", "children")],
            [Input("pangenome_hidden", 'children'),
             Input("zoom-out-switch", "on"),
             Input("poagraph-slider", "value"),
             Input("poagraph_dropdown", "value"),
             Input("poagraph_node_dropdown", "value"),
             Input("consensus_tree_graph", 'clickData'),
             Input("poagraph_checklist", 'value'),
             Input("poagraph_threshold", 'value')],
            [State("full_consensustable_hidden", 'children'),
             State("full_consensustree_hidden", 'children')]
        )(self.get_sankey_diagram)
        app.callback(
            [Output("poagraph-slider", "max"),
             Output("poagraph-slider", "marks")],
            [Input("pangenome_hidden", 'children')]
        )(self.set_slider)
        app.callback(
            Output("poagraph-simplifications", "style"),
            [Input("zoom-out-switch", "on")]
        )(lambda x: {"visibility": "hidden"} if x else {})
        app.callback(
            Output("poagraph-slider", "value"),
            [Input("poagraph_region_button", 'n_clicks')],
            [State("poagraph_start", 'value'),
             State("poagraph_end", 'value')]
        )(lambda x, start, end: [start, end])
        app.callback(
            [Output("poagraph_start", 'value'),
             Output("poagraph_end", 'value')],
            [Input("poagraph-slider", "value")]
        )(lambda x: (x[0], x[1]))
    
    def update_data(self, data):
        self.column_dict = self.c_dict(data["nodes"])
        self.consensus_sequence = data["affinitytree"][0]["nodes_ids"]
        self.nodes = self.get_nodes(data["nodes"])
        self.sequences = {sequence["sequence_str_id"]: sequence["nodes_ids"][0] for sequence in data["sequences"]}
        self.diagram = self.construct_diagram()
            
    def get_nodes(self, nodes_data):
        nodes_list = list()
        for node in nodes_data:
            column = self.column_dict[node["column_id"]]
            for n in column:
                if n in self.consensus_sequence:
                    column.remove(n)
                    column.insert(0, n)
            
            nodes_list.append(
                Node(
                    idx = node["id"], 
                    base = node["base"],
                    column = node["column_id"],
                )
            )
        return nodes_list
                
    def c_dict(self, nodes_data):
        column_dict = dict()
        for node in nodes_data:
            if node["column_id"] not in column_dict:
                column_dict[node["column_id"]] = []
            column_dict[node["column_id"]].append(node["id"])
        return column_dict

    def set_slider(self, hidden):
        slider_max = len(self.column_dict)-1 if self.column_dict else 100
        slider_marks = {i: {"label": str(i)} for i in range(0, slider_max, 100)}
        return slider_max, slider_marks
    
    def find_gaps(self):
        gaps = [0]*len(self.column_dict)
        for sequence in self.sequences:
            i=0
            if len(self.sequences[sequence]) < len(gaps):
                for node_id in self.sequences[sequence]:
                    while self.nodes[node_id].column > i:
                        gaps[i] += 1
                        i += 1
                    i += 1
        return [gap/len(self.sequences) for gap in gaps]

    def construct_diagram(self, sequences_values=None):
        diagram_nodes = dict()
        sequences_values = sequences_values if sequences_values else self.sequences.values()
        for sequence in sequences_values:
            for i, node_id in enumerate(sequence[:-2]):
                source = self.nodes[node_id].id
                target = self.nodes[sequence[i+1]].id

                # SOURCE
                if node_id in diagram_nodes:
                    if target in diagram_nodes[node_id]["targets"]:
                        diagram_nodes[node_id]["targets"][target] += 1
                    else:
                        diagram_nodes[node_id]["targets"][target] = 1
                else:
                    diagram_nodes[node_id] = dict(
                        base = self.nodes[node_id].base,
                        sources = {},
                        targets = {target: 1},
                    )
                # TARGET
                if target in diagram_nodes:
                    if node_id in diagram_nodes[target]["sources"]:
                        diagram_nodes[target]["sources"][node_id] += 1
                    else:
                        diagram_nodes[target]["sources"][node_id] = 1
                else:
                    diagram_nodes[target] = dict(
                        base = self.nodes[target].base,
                        sources = {node_id: 1},
                        targets = {},
                    )
        return diagram_nodes
    
    def _bound_vertices(self, diagram, range_start, range_end):
        diagram_reorganization = dict()
        for node_id in sorted(diagram.keys())[range_start:range_end+1]:
            node = diagram[node_id]
            if len(node["sources"]) == 1:
                source_id = list(node["sources"].keys())[0]
                source_value = node["sources"][source_id]
                while source_id in diagram_reorganization:
                    source_id = diagram_reorganization[source_id]
                diagram[node_id]["sources"] = {source_id: source_value}
                if source_id >= range_start and len(diagram[source_id]["targets"]) == 1:
                    diagram_reorganization[node_id] = source_id
                    diagram[source_id]["base"] += diagram[node_id]["base"]
                    diagram[source_id]["targets"] = diagram[node_id]["targets"]
                    diagram[node_id]["sources"] = {}
                    diagram[node_id]["targets"] = {}
        return diagram, diagram_reorganization

    def _remove_snp(self, consensus, sequence):
        filtered_sequence = [sequence[0]]
        for i, node_id in enumerate(sequence[1:-1]):
            # SUBSTITUTION AND INSERTION
            if node_id not in consensus and sequence[i] in consensus and sequence[i+2] in consensus:
                before = consensus.index(sequence[i])
                after = consensus.index(sequence[i+2])
                if after-before == 1:  # INSERTION
                    pass
                elif after-before == 2:  # SUBSTITUTION
                    filtered_sequence.append(consensus[before+1])
                else:
                    filtered_sequence.append(node_id)
            # DELETION
            elif node_id in consensus and sequence[i+2] in consensus:
                before = consensus.index(sequence[i+1])
                after = consensus.index(sequence[i+2])
                if after-before == 2:  # DELETION
                    filtered_sequence.append(node_id)
                    filtered_sequence.append(consensus[before+1])
                else:
                    filtered_sequence.append(node_id)
            else:
                filtered_sequence.append(node_id)
        filtered_sequence.append(sequence[-1])
        return filtered_sequence
            

    def get_sankey_diagram(self, hidde, zoom_out, slider_values, highlight_seq, tree_node, click_data, checklist, threshold, consensustable_data, consensustree_data):
        if not self.sequences:
            raise PreventUpdate()
        
        # RANGE START / END
        range_start = min(self.column_dict[slider_values[0]])
        range_end = max(self.column_dict[slider_values[1]]) if slider_values[1] in self.column_dict else len(self.diagram)
            
        label = []
        source = []
        target = []
        value = []
        link_color = []
        colors=dict(A="#FF9AA2", C="#B5EAD7", G="#C7CEEA", T="#FFDAC1")
        
        
        # FILTER SEQUENCES (AFFINITY TREE)
        if tree_node or click_data:
            if tree_node:
                tree_node_id = int(tree_node[5:])
            else:
                tree_node_id = click_data['points'][0]['pointIndex']
            full_consensustable = pd.read_json(consensustable_data)
            consensustree_data = json.loads(consensustree_data)
            tree = consensustree.dict_to_tree(consensustree_data)
            node_details_df = consensustable.get_consensus_details_df(tree_node_id, full_consensustable, tree)
            filtered_sequences = node_details_df["SEQID"].tolist()
            diagram_filtered = self.construct_diagram(sequences_values=[self.sequences[seq] for seq in filtered_sequences])
            
            for i in range(len(self.column_dict)):
                if i not in diagram_filtered:
                    diagram_filtered[i] = dict(
                        base = "",
                        sources = {},
                        targets = {},
                    )
        else:
            tree_node_id = None
            filtered_sequences = list(self.sequences.keys())
            diagram_filtered = copy.deepcopy(self.diagram)
        
        if zoom_out:  # EXTREAME ZOOM-OUT
            checklist = [1, 2]
            threshold = len(self.sequences)*0.2
            range_start = 0
            range_end = len(self.column_dict)-1

        if 3 in checklist:
            sequences_values = [self.sequences[seq] for seq in filtered_sequences]
            new_sequences_values = [self._remove_snp(self.consensus_sequence, sequence) for sequence in sequences_values]
            diagram_filtered = self.construct_diagram(sequences_values=new_sequences_values)
            for i in range(len(self.diagram)):
                if i not in diagram_filtered:
                    diagram_filtered[i] = dict(
                        base = "",
                        sources = {},
                        targets = {},
                    )

        if 2 in checklist and threshold > 0:  # WEAK CONNECTIONS                
            weak_nodes = list()
            for node_id in sorted(diagram_filtered.keys())[range_start:range_end+1]:
                node = diagram_filtered[node_id]
                if node["sources"] and (all([x in weak_nodes for x in node["sources"].keys()]) or all([x<=threshold for x in node["sources"].values()])):
                    weak_nodes.append(node_id)
                    diagram_filtered[node_id]["sources"] = {}
                    diagram_filtered[node_id]["targets"] = {}
                else:
                    diagram_filtered[node_id]["sources"] = {key: value for key, value in node["sources"].items() if value>threshold}
                    diagram_filtered[node_id]["targets"] = {key: value for key, value in node["targets"].items() if value>threshold}
            
            for node_id in sorted(diagram_filtered.keys())[range_end-1:range_start:-1]:
                node = diagram_filtered[node_id]
                if node["targets"] and all([x in weak_nodes for x in node["targets"].keys()]):
                    weak_nodes.append(node_id)
                    diagram_filtered[node_id]["sources"] = {}
                    diagram_filtered[node_id]["targets"] = {}
                else:
                    diagram_filtered[node_id]["sources"] = {key: value for key, value in node["sources"].items() if key not in weak_nodes}
                    diagram_filtered[node_id]["targets"] = {key: value for key, value in node["targets"].items() if key not in weak_nodes}


        if 1 in checklist:  # CONCAT VERTICLES
            diagram_filtered, diagram_reorganization = self._bound_vertices(diagram_filtered, range_start, range_end)
        else:
            diagram_reorganization = dict()

        if highlight_seq and highlight_seq in filtered_sequences:  # HIGHLIGHT SEQUENCE
            highlight_seq_nodes = [node_id for node_id in self.sequences[highlight_seq] if node_id not in diagram_reorganization.keys()]
        else:
            highlight_seq_nodes = []
        
        for node_id in sorted(diagram_filtered.keys())[range_start:range_end+1]:
            label.append(diagram_filtered[node_id]["base"])
            for t in diagram_filtered[node_id]["targets"]:
                if t <= range_end:
                    source.append(node_id-range_start)
                    target.append(t-range_start)
                    value.append(diagram_filtered[node_id]["targets"][t])
                    link_color.append("#D3D3D3")
                    
                    # HIGHLIGHT SEQUENCE
                    if highlight_seq_nodes and node_id in highlight_seq_nodes:
                        s_id = highlight_seq_nodes.index(node_id)
                        if highlight_seq_nodes[s_id+1] == t:
                            value[-1] -= 1
                            source.append(node_id-range_start)
                            target.append(t-range_start)
                            value.append(1)
                            link_color.append("#342424")

        
        colors = dict(A="#FF9AA2", C="#B5EAD7", G="#C7CEEA", T="#FFDAC1")
        #extra dump node
        if len(source) == 0:
            label.append("start")
            label.append("end")
            source.append(len(label)-2)
            target.append(len(label)-1)
            value.append(len(filtered_sequences))
            link_color.append("#D3D3D3")
            
        fig = go.Figure(
            data=go.Sankey(
                arrangement = "snap",
                node = dict(
                    thickness=max(10, 26-(len(label)//10)),
                    label=[l if len(l)<6 else f"{l[0]}...{l[-1]}({len(l)})" for l in label],
                    pad=10,
                    color=[colors[l] if l in colors else get_color_for_merged_node(l) for l in label]
                ),
                link = dict(
                    source=source,
                    target=target,
                    value=value,
                    color=link_color
                )
            ),
            layout=dict(
                # height=300,
                # width=1600
            )
        )
        
        return fig, str(tree_node_id) 

def get_color_for_merged_node(label):
    intensity = max(200-len(label)*15, 80)
    return f"rgb({intensity},{intensity},{intensity})"

alignment_main_object = GraphAlignment(data={})
