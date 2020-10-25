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
    def __init__(self, idx, base, x, y):
        self.id = idx
        self.base = base
        self.x = x
        self.y = y
        
    def __repr__(self):
        return f"{self.base} ID: {self.id} <{self.x},{self.y}>"


class GraphAlignment:
    def __init__(self, data):
        self.column_dict = None
        self.consensus_sequence = None
        self.nodes = None
        self.sequences = None
        self.gaps = None
        self.diagram = None
        app.callback(
            [Output("poagraph", "figure"),
             Output("gap-shape_x", "data"),
             Output("selected_vertex", "children")],
            [Input("full_pangenome_graph", "relayoutData"),
             Input("pangenome_hidden", 'children'),
             Input("zoom-out-switch", "on"),
             Input("poagraph-slider", "value"),
             Input("poagraph_dropdown", "value"),
             Input("consensus_tree_graph", 'clickData'),
             Input("poagraph_checklist", 'value'),
             Input("poagraph_threshold", 'value')],
            [State("full_consensustable_hidden", 'children'),
             State("full_consensustree_hidden", 'children'),
             State("gap-shape_x", "data")]
        )(self.get_sankey_diagram)
        app.callback(
            Output("full_pangenome_graph", "figure"),
            [Input("pangenome_hidden", 'children'),
             Input("gap-shape_x", "data")]
        )(self.get_gap_graph)
        app.callback(
            Output("poagraph-simplifications", "style"),
            [Input("zoom-out-switch", "on")]
        )(lambda x: {"visibility": "hidden"} if x else {})

    def update_data(self, data):
        self.column_dict = self.c_dict(data["nodes"])
        self.consensus_sequence = data["affinitytree"][0]["nodes_ids"]
        self.nodes = self.get_nodes(data["nodes"])
        self.sequences = {sequence["sequence_str_id"]: sequence["nodes_ids"][0] for sequence in data["sequences"]}
        self.gaps = self.find_gaps()
        self.diagram = self.construct_diagram()
            
    def get_nodes(self, nodes_data):
        nodes_list = list()
        for node in nodes_data:
            column = self.column_dict[node["column_id"]]
            for n in column:
                if n in self.consensus_sequence:
                    column.remove(n)
                    column.insert(0, n)
            node_y = 0
            if column.index(node["id"]) == 1:
                node_y = -1
            elif column.index(node["id"]) == 2:
                node_y = 1
            elif column.index(node["id"]) >= 3:
                node_y = -2
            
            nodes_list.append(
                Node(
                    idx = node["id"], 
                    base = node["base"],
                    x = node["column_id"],
                    y = node_y
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
    
    def find_gaps(self):
        gaps = [0]*len(self.column_dict)
        for sequence in self.sequences:
            i=0
            if len(self.sequences[sequence]) < len(gaps):
                for node_id in self.sequences[sequence]:
                    while self.nodes[node_id].x > i:
                        gaps[i] += 1
                        i += 1
                    i += 1
        return [gap/len(self.sequences) for gap in gaps]
           
    def get_gap_graph(self, is_ready, shape_x):
        if not is_ready or not self.gaps:
            raise PreventUpdate()

        fig = go.Figure(
            data = [
                go.Bar(
                    x=list(range(len(self.gaps))), 
                    y=self.gaps,
                    marker_color="#484848",
                )
            ],
            layout = dict(
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                dragmode="zoom",
                hovermode=False,
                legend=dict(traceorder="reversed"),
                template="plotly_white",
                title=dict(
                    text="Gap"
                ),
                margin=dict(
                    t=100,
                    b=100
                ),
                xaxis=dict(
                    range= [0, len(self.gaps)],
                    fixedrange= True,
                    showgrid= False,
                    zeroline= False,
                    visible= False,
                ),
                yaxis=dict(
                    range= [0, 1],
                    fixedrange= True,
                    visible= True,
                )
            )
        )

        fig.add_shape(
            x0=shape_x[0], 
            x1=shape_x[1], 
            y0=-100, 
            y1=100,
            fillcolor="#75bba7",
            line_color="#75bba7",
            opacity=0.2,
        )

        return fig

    def construct_diagram(self, sequences=None):
        diagram_nodes = dict()
        sequences_values = [self.sequences[seq] for seq in sequences] if sequences else self.sequences.values()
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

    def get_sankey_diagram(self, relayout_data, hidde, zoom_out, max_columns, highlight_seq, click_data, checklist, threshold, consensustable_data, consensustree_data, gap_shape):
        if not self.sequences:
            raise PreventUpdate()
        
        # RANGE START / END
        range_start = max(0, gap_shape[0])
        range_end = min(range_start+max_columns, len(self.column_dict)-1)
        if relayout_data and "shapes[0].x0" in relayout_data.keys():
            range_start = max(int(relayout_data["shapes[0].x0"]), 0)
            range_end = min(int(relayout_data["shapes[0].x1"]), range_start+range_end, len(self.column_dict)-1)

        gap_shape = dash.no_update if gap_shape==[range_start, range_end] else [range_start, range_end]
        range_start = min(self.column_dict[range_start])
        range_end = max(self.column_dict[range_end])
            
        label = []
        source = []
        target = []
        value = []
        link_color = []
        colors=dict(A="#FF9AA2", C="#B5EAD7", G="#C7CEEA", T="#FFDAC1")
        
        
        # FILTER SEQUENCES (AFFINITY TREE)
        if click_data:
            tree_node_id = click_data['points'][0]['pointIndex']
            full_consensustable = pd.read_json(consensustable_data)
            consensustree_data = json.loads(consensustree_data)
            tree = consensustree.dict_to_tree(consensustree_data)
            node_details_df = consensustable.get_consensus_details_df(tree_node_id, full_consensustable, tree)
            filtered_sequences = node_details_df["SEQID"].tolist()
            diagram_filtered = self.construct_diagram(sequences=filtered_sequences)
            
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
            gap_shape = [range_start, range_end]

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
                if all([x in weak_nodes for x in node["targets"].keys()]):
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
                    
                    # HIGHLIGHT SEQUENCE
                    if highlight_seq_nodes and node_id-range_start in highlight_seq_nodes:
                        s_id = highlight_seq_nodes.index(node_id-range_start)
                        if highlight_seq_nodes[s_id+1] == t-range_start:
                            link_color.append("#342424")
                        else:
                            link_color.append("#D3D3D3")
                    else:
                        link_color.append("#D3D3D3")
        
        colors = dict(A="#FF9AA2", C="#B5EAD7", G="#C7CEEA", T="#FFDAC1")
        fig = go.Figure(
            data=go.Sankey(
                arrangement = "snap",
                node = dict(
                    label=[l if len(l)<5 else f"{l[0]}...{l[-1]}({len(l)})" for l in label],
                    pad=10,
                    color=[colors[l] if l in colors else "gray" for l in label]
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
        
        return fig, gap_shape, str(tree_node_id) 

alignment_main_object = GraphAlignment(data={})
