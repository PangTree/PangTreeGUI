from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

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
        app.callback(
            Output("poagraph", "figure"),
            [Input("full_pangenome_graph", "relayoutData"),
             Input("full_pangenome_graph", "figure"),
             Input("poagraph_dropdown", "value")],
        )(self.get_poagraph_fragment)
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

    # def get_nodes_old(self, nodes_data, nodes_ids):
    #     nodes = list()
    #     i = 0
    #     for node in nodes_data:
    #         if node["id"] in nodes_ids:
    #             column = self.column_dict[node["column_id"]]
    #             while i < node["column_id"]:
    #                 nodes.append(
    #                     Node(
    #                         idx = None, 
    #                         base = None,
    #                         x = None,
    #                         y = None
    #                     )
    #                 )
    #                 i += 1
    #             nodes.append(
    #                 Node(
    #                     idx = node["id"], 
    #                     base = node["base"],
    #                     x = node["column_id"],
    #                     y = (column.index(node["id"])+1)/(len(column)+1)
    #                 )
    #             )
    #             i += 1
    #     return nodes
                
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
        return [gap/len(self.column_dict) for gap in gaps]
           
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
            x1=50, 
            y0=-100, 
            y1=100,
            fillcolor="#75bba7",
            line_color="#75bba7",
            opacity=0.2,
        )

        return fig

    def get_node_coordinates(self, node):
        return node.x, node.y, node.base

    def get_poagraph_traces(self, range_start, range_end, sequences=[]):
        trace_dict = dict()
        if sequences:
            filtered_sequences = [self.sequences[seq] for seq in sequences]
        else:
            filtered_sequences = self.sequences.values()
        for sequence in filtered_sequences:
            for i in range(range_start, min(range_end, len(sequence))-2):  
                x0, y0, base0 = self.get_node_coordinates(self.nodes[sequence[i]])
                x1, y1, base1 = self.get_node_coordinates(self.nodes[sequence[i+1]])
                trace_key = f"{x0},{y0},{base0},{x1},{y1},{base1}"
                if x0 and x1 and trace_key not in trace_dict.keys():
                    trace_dict[trace_key] = 1
                elif x0 and x1:
                    trace_dict[trace_key] = trace_dict[trace_key]+1
        return trace_dict

    def get_poagraph_fragment(self, relayout_data, poagraph, highlighted_sequence):
        if not self.sequences:
            raise PreventUpdate()

        if relayout_data and "shapes[0].x0" in relayout_data.keys():
            range_start = max(int(relayout_data["shapes[0].x0"]), 0)
            range_end = min(int(relayout_data["shapes[0].x1"]), range_start+50, len(self.column_dict))
        else:
            range_start = 0
            range_end = min(50, len(self.column_dict))

        print(f"{range_start}, {range_end}")
        fig = go.Figure()
        trace_dict = self.get_poagraph_traces(range_start, range_end)
        max_value = max(trace_dict.values())
        colors = {"A": "#f1c5c5", "C": "#fdcb9e", "G": "#bbd196", "T": "#8bcdcd"}
        for key, value in trace_dict.items():
            x0, y0, base0, x1, y1, base1 = key.split(",")
            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                # name=seq,
                mode="lines+markers+text",
                text=[base0, base1],
                yaxis="y",
                hoverinfo="name+x+text",
                line={"width": value*6./max_value+2, "color": "#d3d3d3"},
                marker={
                    "size": 30, 
                    "color": [colors[base0], colors[base1]], 
                    "line": 
                    {
                        # "width": 3, 
                        # "color": [colors[base0], colors[base1]]
                    }},
                showlegend=False
            ))

        if highlighted_sequence:
            highlighted_trace = self.get_poagraph_traces(range_start, range_end, [highlighted_sequence])
            for key, value in highlighted_trace.items():
                x0, y0, base0, x1, y1, base1 = key.split(",")
                fig.add_trace(go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    # name=seq,
                    mode="markers+text",
                    text=[base0, base1],
                    # line={"width": 2},
                    marker={
                        "size": 30, 
                        "color": [colors[base0], colors[base1]], 
                        "line": 
                        {
                            "width": 3, 
                            "color": "black"
                        }},
                    showlegend=False
                ))

        fig.update_layout(
            # width=1200,
            height=500,
            dragmode="zoom",
            hovermode=False,
            legend=dict(traceorder="reversed"),
            template="plotly_white",
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(
                t=30,
                b=50
            ),
            xaxis=dict(
                showgrid= False,
                zeroline= False,
                visible= False,
                range= [range_start-0.4, range_end-2+0.4],
            ),
            yaxis=dict(
                visible= False,
            )
        )

        return fig

alignment_main_object = GraphAlignment(data={})
