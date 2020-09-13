import json
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
            Output("poagraph", "figure"),
            [Input("full_pangenome_graph", "relayoutData"),
             Input("full_pangenome_graph", "figure"),
             Input("poagraph_dropdown", "value"),
             Input("consensus_tree_graph", 'clickData')],
            [State("full_consensustable_hidden", 'children'),
             State("full_consensustree_hidden", 'children')]
        )(self.get_sankey_diagram)
        app.callback(
            Output("full_pangenome_graph", "figure"),
            [Input("pangenome_hidden", 'children')]
        )(self.get_gap_graph)

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
           
    def get_gap_graph(self, is_ready):
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
            x0=0, 
            x1=40, 
            y0=-100, 
            y1=100,
            fillcolor="#75bba7",
            line_color="#75bba7",
            opacity=0.2,
        )

        return fig

    def construct_diagram(self):
        diagram_nodes = dict()
        for sequence in self.sequences.values():
            
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
                        sources = {node_id: 1},
                        targets = {},
                    )
        return diagram_nodes
    
    def get_sankey_diagram(self, relayout_data, poagraph, highlighted_sequence, click_data, consensustable_data, consensustree_data):
        if not self.sequences:
            raise PreventUpdate()
        
        # RANGE START / END
        range_start = 0
        range_end = min(40, len(self.column_dict))
        if relayout_data and "shapes[0].x0" in relayout_data.keys():
            range_start = max(int(relayout_data["shapes[0].x0"]), 0)
            range_end = min(int(relayout_data["shapes[0].x1"]), range_start+40, len(self.column_dict))
        range_start = min(self.column_dict[range_start])
        range_end = max(self.column_dict[range_end])

        # FILTER SEQUENCES (AFFINITY TREE)
        # if click_data:
        #     node_id = click_data['points'][0]['pointIndex']
        #     full_consensustable = pd.read_json(consensustable_data)
        #     consensustree_data = json.loads(consensustree_data)
        #     tree = consensustree.dict_to_tree(consensustree_data)
        #     node_details_df = consensustable.get_consensus_details_df(node_id, full_consensustable, tree)
        #     diagram = self.construct_diagram(sequences=node_details_df["SEQID"].tolist())
        # else:
        #     diagram = self.diagram
            
        zoom=1

        label = []
        source = []
        target = []
        value = []
        colors=dict(A="#FF9AA2", C="#B5EAD7", G="#C7CEEA", T="#FFDAC1")
        
        
        if zoom == 0:
            for node_id in sorted(self.diagram.keys())[range_start:range_end+1]:
                label.append(self.nodes[node_id].base)
                for t in self.diagram[node_id]["targets"]:
                    if t <= range_end:
                        source.append(node_id-range_start)
                        target.append(t-range_start)
                        value.append(self.diagram[node_id]["targets"][t])
        
        # CONCAT NODES            
        elif zoom == 1:
            for node_id in sorted(self.diagram.keys())[range_start:range_end+1]:
                node = self.diagram[node_id]
                label.append(self.nodes[node_id].base)            
                    
                if len(node["sources"]) == 1 and sum(node["sources"].values()) == len(self.sequences):
                    source_id = list(node["sources"].keys())[0]
                    node_source = self.diagram[source_id]
                    while len(node_source["sources"]) == 1 and sum(node_source["sources"].values()) == len(self.sequences):
                        source_id = list(node_source["sources"].keys())[0]
                        node_source = self.diagram[source_id]
                    label[source_id-range_start] += self.nodes[node_id].base
                    if len(node["targets"]) != 1 or sum(node["targets"].values()) != len(self.sequences):
                        for t in node["targets"]:
                            if t <= range_end:
                                source.append(source_id-range_start)
                                target.append(t-range_start)
                                value.append(self.diagram[node_id]["targets"][t])
                
                elif len(node["targets"]) != 1 or sum(node["targets"].values()) != len(self.sequences):
                    for t in self.diagram[node_id]["targets"]:
                        if t <= range_end:
                            source.append(node_id-range_start)
                            target.append(t-range_start)
                            value.append(self.diagram[node_id]["targets"][t])            
        
        colors = dict(A="#FF9AA2", C="#B5EAD7", G="#C7CEEA", T="#FFDAC1")
        fig = go.Figure(
            data=go.Sankey(
                arrangement = "snap",
                node = dict(
                    label=label,
                    pad=10,
                    color=[colors[l] if l in colors else "gray" for l in label]
                ),
                link = {
                    "source": source,
                    "target": target,
                    "value": value
                }
            ),
            layout=dict(
                # height=300,
        #         width=1600
            )
        )
        
        return fig

alignment_main_object = GraphAlignment(data={})
