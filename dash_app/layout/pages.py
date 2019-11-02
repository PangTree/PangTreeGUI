import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from pangtreebuild.output.PangenomeJSON import PangenomeJSON

from .layout_ids import *
import dash_cytoscape as cyto
import dash_table
from ..components import mafgraph as mafgraph_component
from ..components import poagraph as poagraph_component


def contact():
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H5("Norbert Dojer, PhD.", className="card-title text-info"),
                html.P("dojer@mimuw.edu.pl", className='card-text'),
            ]),
        ], outline=True, color="info"),
        dbc.Card([
            dbc.CardBody([
                html.H5("Paulina Dziadkiewicz, M.Sc.", className="card-title text-info"),
                html.P("pedziadkiewicz@gmail.com", className='card-text'),
            ])
        ], outline=True, color="info"),
        dbc.Card([
            dbc.CardBody([
                html.H5("Paulina Knut, B.Sc.", className="card-title text-info"),
                html.P("paulina.knut@gmail.com", className='card-text'),
            ])
        ], outline=True, color="info")
    ])


def index():
    return dbc.Container(
        html.Div([
            dbc.Jumbotron(children=[dbc.Row(
                [dbc.Col([html.H2("PangtreeBuild"),
                          html.P("is a tool for multiple sequence alignment analysis."),
                          html.H2("PangtreeVis"),
                          html.P("visualises the results of PangtreeBuild in browser.")
                          ],
                         className="col-md-8"),
                 dbc.Col(html.I(className="fas fa-seedling fa-10x logo"), className="col-md-4")])]),
            dbc.Row(
                dbc.CardDeck(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(dbc.Row([dbc.Col(html.I(className="fas fa-bezier-curve fa-2x"),
                                                                className="col-md-3 my-auto"),
                                                        html.P(
                                                            "Build graph representation of multiple sequence alignment",
                                                            className="col-md-9 my-auto")])),
                                dbc.CardBody(
                                    [
                                        dbc.CardText(
                                            html.Ul([html.Li(
                                                ["Input formats: ",
                                                 html.A("MAF",
                                                        href="http://www1.bioinf.uni-leipzig.de/UCSC/FAQ/FAQformat.html#format5",
                                                        target="_blank"), ", ",
                                                 html.A("PO",
                                                        href="https://github.com/meoke/pangtree/blob/master/Documentation.md#po-file-format-specification",
                                                        target="_blank")]),
                                                html.Li(["Internal representation: ", html.A("Partial Order graph",
                                                                                             href="https://doi.org/10.1093/bioinformatics/18.3.452",
                                                                                             target="_blank")]),
                                                html.Li(["Cycles in graph removed with ", html.A("Mafgraph",
                                                                                                 href="https://github.com/anialisiecka/Mafgraph",
                                                                                                 target="_blank")]),
                                                html.Li("Complement missing parts from NCBI or fasta")]))
                                    ]
                                ),
                            ]
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader(dbc.Row([dbc.Col(html.I(className="fas fa-grip-lines fa-2x"),
                                                                className="col-md-3 my-auto"),
                                                        html.P("Find sequences consensus",
                                                               className="col-md-9 my-auto")])),
                                dbc.CardBody(
                                    [
                                        dbc.CardText(
                                            ["This tool extends Partial Order Alignment (POA) algorithm introduced by ",
                                             html.A("Lee et al.",
                                                    href="https://doi.org/10.1093/bioinformatics/18.3.452",
                                                    target="_blank"), ". It provides:",
                                             html.Ul([html.Li([html.Strong("Consensuses"),
                                                               " - agreed representations of input subsets"]),
                                                      html.Li([html.Strong("Affinity Tree"),
                                                               " - a structure similar to phylogenetic tree but it has a consensus assigned to every node"]),
                                                      html.Li([html.Strong("Compatibility"),
                                                               " - a measure of similarity between sequence and consensus"])])
                                             ]),
                                    ]
                                ),
                            ]
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader(dbc.Row([dbc.Col(html.I(className="fas fa-eye fa-2x"),
                                                                className="col-md-3 my-auto"),
                                                        html.P("Visualise results",
                                                               className="col-md-9 my-auto")])),
                                dbc.CardBody(
                                    [
                                        dbc.CardText(
                                            [
                                                html.Ul([
                                                    # html.Li("MAF blocks graph"),
                                                    html.Li("Multiple sequence alignment as Partial Order Graph"),
                                                    html.Li("Affinity tree"),
                                                    html.Li("Compatibilities relations")]
                                                )])
                                    ]
                                ),
                            ]
                        ),
                    ]
                )
            )

        ])
    )


def package():
    return dbc.Container([dbc.Row(html.Span(["The underlying software is available at ",
                                             html.A("GitHub", href="https://github.com/meoke/pangtree",
                                                    target="_blank"),
                                             # " and ",
                                             # html.A("PyPI", href="", target="_blank"),
                                             ". It can be incorporated into your Python application in this simple way:"])),
                          dbc.Card(dbc.CardBody(dcc.Markdown('''

                          
                          from pangtreebuild import Poagraph, input_types, fasta_provider, consensus

                          poagraph = Poagraph.build_from_dagmaf(input_types.Maf("example.maf"), 
                                                                fasta_provider.FromNCBI())
                          affinity_tree = consensus.tree_generator.get_affinity_tree(poagraph,
                                                                                     Blosum("BLOSUM80.mat"),
                                                                                     output_dir,
                                                                                     stop=1,
                                                                                     p=1)
                          pangenomejson = to_PangenomeJSON(poagraph, affinity_tree)
                          
                          ''')), style={"margin": '30px 0px', 'padding': '10px'}),
                          dbc.Row("or used as a CLI tool:"),
                          dbc.Card(dbc.CardBody(dcc.Markdown(
                              '''pangtreebuild --multialignment "example.maf" --consensus tree --p 1 --stop 1''')),
                              style={"margin": '30px 0px', 'padding': '10px'}),
                          dbc.Row("Check out full documentation at the above link.")
                          ]
                         )


def tools():
    return html.Div([
        dbc.Tabs(
            [
                dbc.Tab(_poapangenome_tab_content, id=id_poapangenome_tab, label="PangtreeBuild",
                        tab_style={"margin-left": "auto"}, className="tools_tab"),
                dbc.Tab(_pangviz_tab_content, id=id_pangviz_tab, label="PangtreeVis", label_style={"color": "#00AEF9"},
                        className="tools_tab"),
            ], className="nav-justified",
            id=id_tools_tabs,
        )
    ])


_data_type_form = dbc.FormGroup(
    [
        dbc.Label("Data Type", html_for=id_data_type, width=3, className="poapangenome_label"),
        dbc.Col([dbc.RadioItems(value="Nucleotides", options=[{"label": "Nucleotides", "value": "Nucleotides"},
                                                              {"label": "Aminoacids", "value": "Proteins"}],
                                id=id_data_type),
                 dbc.FormText(
                     "Type of aligned sequences provided in the uploaded multialignment file.",
                     color="secondary",
                 )], width=6)
    ],
    row=True,
    style={"display": "none"}
)

_metadata_upload_form = dbc.FormGroup(
    [
        dbc.Label("Sequences metadata", html_for=id_metadata_upload, width=3, className="poapangenome_label"),
        dbc.Col([dcc.Upload(id=id_metadata_upload,
                            multiple=False,
                            children=[
                                dbc.Row([dbc.Col(html.I(className="fas fa-file-csv fa-2x"),
                                                 className="col-md-2"),
                                         html.P(
                                             "Drag & drop or select file...",
                                             className="col-md-10")])

                            ], className="file_upload"),
                 dcc.Store(id=id_metadata_upload_state),
                 dbc.FormText(
                     [
                         "CSV with sequences metadata. It will be included in the visualisation. "
                         "The 'seqid' column is obligatory and must match"
                         " sequences identifiers from MULTIALIGNMENT file. "
                         "Other columns are optional. Example file: ",
                         html.A("metadata.csv",
                                href="https://github.com/meoke/pangtree/blob/master/data/Fabricated/f_metadata.csv",
                                target="_blank")],
                     color="secondary",
                 )
                 ], width=6),
        dbc.Label(id=id_metadata_upload_state_info, width=3, className="poapangenome_label")
    ],
    row=True
)

_multialignment_upload_form = dbc.FormGroup(
    [
        dbc.Label("Multialignment", html_for=id_multialignment_upload, width=3, className="poapangenome_label"),
        dbc.Col([dcc.Upload(id=id_multialignment_upload,
                            multiple=False,
                            children=[
                                dbc.Row([dbc.Col(html.I(className="fas fa-align-justify fa-2x"),
                                                 className="col-md-2"),
                                         html.P(
                                             "Drag & drop or select file...",
                                             className="col-md-10")])

                            ], className="file_upload"),
                 dcc.Store(id=id_multialignment_upload_state),
                 dbc.FormText(
                     [
                         "Accepted formats: ",
                         html.A(
                             href="http://www1.bioinf.uni-leipzig.de/UCSC/FAQ/FAQformat.html#format5",
                             target="_blank", children="maf"), ", ",
                         html.A(
                             href="https://github.com/meoke/pangtree/blob/master/Documentation.md#po-file-format-specification",
                             target="_blank", children="po"),
                         ". See example file: ",
                         html.A(
                             href="https://github.com/meoke/pangtree/blob/master/data/Ebola/multialignment.maf",
                             target="_blank",
                             children="example.maf")],
                     color="secondary",
                 )
                 ], width=6),
        dbc.Label(id=id_multialignment_upload_state_info, width=3, className="poapangenome_label")
    ],
    row=True
)

_missing_data_form = dbc.Collapse([dbc.FormGroup(
    [
        dbc.Label("Missing nucleotides source", html_for=id_fasta_provider_choice, width=3,
                  className="poapangenome_label"),
        dbc.Col([dbc.RadioItems(value="NCBI", options=[{'label': "NCBI", 'value': 'NCBI'},
                                                       {'label': 'Fasta File',
                                                        'value': 'File'},
                                                       {'label': 'Custom symbol',
                                                        'value': 'Symbol'}],
                                id=id_fasta_provider_choice),
                 dbc.FormText(
                     "MAF file may not include full sequences. Specify source of missing nucleotides.",
                     color="secondary",
                 )], width=6)
    ],
    row=True
), dbc.Collapse(id=id_missing_symbol_param, children=[dbc.FormGroup(
    children=[
        dbc.Label("Missing symbol for unknown nucleotides", html_for=id_fasta_provider_choice,
                  width=3, className="poapangenome_label"),
        dbc.Col([dbc.Input(value="?",
                           id=id_missing_symbol_input, type='text', maxLength=1, minLength=1),
                 dbc.FormText(
                     "Any single character is accepted but it must be present in BLOSUM file. Default BLOSUM file uses '?'.",
                     color="secondary",
                 )], width=6)], row=True
)]),
    dbc.Collapse(id=id_fasta_upload_param, children=[dbc.FormGroup(
        children=[
            dbc.Label("Missing symbols file source", html_for=id_fasta_provider_choice,
                      width=3, className="poapangenome_label"),
            dbc.Col([dcc.Upload(id=id_fasta_upload,
                                multiple=False,
                                children=[
                                    dbc.Row([dbc.Col(html.I(className="fas fa-align-left fa-2x"),
                                                     className="col-md-2"),
                                             html.P(
                                                 "Drag & drop or select file...",
                                                 className="col-md-10")])

                                ], className="file_upload"),
                     dcc.Store(id=id_fasta_upload_state),
                     dbc.FormText(
                         [
                             "Provide zip with fasta files or single fasta file. It must contain all full sequeneces which are not fully represented in provided MAF file."],
                         color="secondary",
                     )
                     ], width=6),
            dbc.Label(id=id_fasta_upload_state_info, width=3, className="poapangenome_label")], row=True
    )])
], id=id_maf_specific_params)

_consensus_algorithm_form = dbc.FormGroup(
    [
        dbc.Label("Affinity tree algorithm", html_for=id_data_type, width=3, className="poapangenome_label"),
        dbc.Col([dbc.RadioItems(value="tree", options=[
            {'label': "Poa", 'value': 'poa'},
            {'label': 'Tree', 'value': 'tree'},
        ],
                                id=id_consensus_algorithm_choice),
                 dbc.FormText(
                     [
                         "There are two available algorithms for affinity tree generation. 'Poa' by ",
                         html.A(
                             "Lee et al.",
                             href="https://doi.org/10.1093/bioinformatics/btg109"),
                         " and 'Tree' algorithm described ",
                         html.A("here",
                                href="https://github.com/meoke/pangtree/blob/master/Documentation.md#idea-and-algorithm-description")],
                     color="secondary",
                 )], width=6)
    ],
    row=True
)

_blosum_upload_form = dbc.FormGroup(
    [
        dbc.Label("BLOSUM", html_for=id_blosum_upload, width=3, className="poapangenome_label"),
        dbc.Col([dcc.Upload(id=id_blosum_upload,
                            multiple=False,
                            children=[
                                dbc.Row([dbc.Col(html.I(className="fas fa-table fa-2x"),
                                                 className="col-md-2"),
                                         html.P(
                                             "Drag & drop or select file...",
                                             className="col-md-10")])

                            ], className="file_upload"),
                 dcc.Store(id=id_blosum_upload_state),
                 dbc.FormText(
                     [
                         "This parameter is optional as default BLOSUM file is ", html.A(
                         href="https://github.com/meoke/pangtree/blob/master/bin/blosum80.mat",
                         target="_blank", children="BLOSUM80"),
                         ". The BLOSUM matrix must contain '?' or the custom symbol for missing nucleotides, if specified."],
                     color="secondary",
                 )
                 ], width=6),
        dbc.Label(id=id_blosum_upload_state_info, width=3, className="poapangenome_label")
    ],
    row=True
)

_poa_hbmin_form = dbc.Collapse([dbc.FormGroup(
    [
        dbc.Label("HBMIN", html_for=id_hbmin_input, width=3,
                  className="poapangenome_label"),
        dbc.Col([dbc.Input(value=0.9, type='number', min=0, max=1,
                           id=id_hbmin_input),
                 dbc.FormText(
                     "HBMIN is required minimum value of similarity between sequence and assigned consensus. It must be a value  from range [0,1].",
                     color="secondary",
                 )], width=6)
    ],
    row=True
)
], id=id_poa_specific_params)

_tree_params_form = dbc.Collapse([dbc.FormGroup([
    dbc.Label("P", html_for=id_hbmin_input, width=3,
              className="poapangenome_label"),
    dbc.Col([dbc.Input(value=1, type='number', min=0,
                       id=id_p_input),
             dbc.FormText(
                 [
                     "P is used during cutoff search. P < 1 decreases distances between small compatibilities and increases distances between the bigger ones while P > 1 works in the opposite way. This value must be > 0. ",
                     html.A("Read more...",
                            href="https://github.com/meoke/pangtree",
                            target="_blank")],
                 color="secondary",
             )], width=6)
],
    row=True), dbc.FormGroup([
    dbc.Label("Stop", html_for=id_hbmin_input, width=3,
              className="poapangenome_label"),
    dbc.Col([dbc.Input(value=1, type='number', min=0, max=1,
                       id=id_stop_input),
             dbc.FormText(
                 "Minimum value of compatibility in affinity tree leaves. It must be a value  from range [0,1].",
                 color="secondary",
             )], width=6)
],
    row=True)], id=id_tree_specific_params)

_output_form = dbc.FormGroup(
    [
        dbc.Label("Additional output generation", html_for=id_output_configuration, width=3,
                  className="poapangenome_label"),
        dbc.Col([dbc.Checklist(id=id_output_configuration,
                               options=[
                                   {
                                       'label': 'FASTA (all sequences and consensuses in fasta format)',
                                       'value': 'fasta'},
                                   {'label': 'PO (poagraph in PO format)', 'value': 'po'},
                               ],
                               values=['fasta', 'po'])], width=6)
        ,
    ], row=True
)

_poapangenome_form = dbc.Form([
    _data_type_form,
    _metadata_upload_form,
    _multialignment_upload_form,
    _missing_data_form,
    _blosum_upload_form,
    _consensus_algorithm_form,
    _poa_hbmin_form,
    _tree_params_form,
    _output_form
])

_poapangenome_tab_content = html.Div([
    dcc.Store(id=id_session_state),
    dcc.Store(id=id_session_dir),
    dbc.Row([
        dbc.Col(
            [
                html.H3("Task Parameters"),
                _poapangenome_form,
                dbc.Row(
                    dbc.Col(dbc.Button("Run", id=id_pang_button, color="primary", className="offset-md-5 col-md-4 ")),
                    dbc.Col(dcc.Loading(id="l2", children=html.Div(id=id_running_indicator), type="default")))
            ], className="col-md-6 offset-md-1", id='poapangenome_form'),
        dbc.Col([
            html.H3("Example Input Data"),
            # dbc.Card(
            #     [
            #         dbc.CardHeader(
            #             dbc.Button("Simulated", id="collapse_simulated_button",
            #                        className="mb-3 btn-block my-auto opac-button")),
            #         dbc.Collapse(
            #             id="simulated_collapse",
            #             children=
            #             dbc.CardBody(
            #                 [
            #                     dbc.CardText(["This dataset is very small and consists of simulated sequences."
            #                                   "Its aim is to demonstrate how the processing and visualisation works",
            #                                   html.Button("a", className="btn btn-primary btn-block dataset")]),
            #                 ]
            #             )),
            #     ]
            # ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Button("Ebola", id="collapse-ebola-button",
                                   className="mb-3 btn-block my-auto opac-button")),
                    dbc.Collapse(
                        id="ebola_collapse",
                        children=dbc.CardBody(
                            [
                                html.P(["This dataset orginates from ", html.A("UCSC Ebola Portal",
                                                                               href="https://genome.ucsc.edu/ebolaPortal/",
                                                                               target="_blank")],
                                       className='card-text'),
                                html.P([html.A(
                                    href="https://github.com/meoke/pangtree/blob/master/data/Ebola/multialignment.maf",
                                    target="_blank",
                                    children="See example file...")], className='card-text'),
                            ]
                        ))
                ],
            ),
        ], className="col-md-3 offset-md-1")
    ], className="poapangenome_content"),
    dbc.Collapse(id=id_poapangenome_result, children=dbc.Row(
        children=[dbc.Col([dbc.Row([html.I(id=id_result_icon), html.H3("Task completed!", className="next_to_icon")]),
                           dbc.Col(html.Div(id=id_poapangenome_result_description), className="col-md-11")],
                          className="col-md-6 offset-md-1"),
                  dbc.Col([
                      html.A(dbc.Button("Download result files", block=True, className="result_btn", color="info"),
                             id=id_download_processing_result),
                      dbc.Button("Go to visualisation", id=id_go_to_vis_tab,
                                 n_clicks_timestamp=0, block=True, className="result_btn", color="success",
                                 style={"visibility": "hidden"})],
                      className="col-md-3 offset-md-1")]

    ))
])

_load_pangenome_row = dbc.Row(id=id_pangviz_load_row,
                              children=[
                                  dbc.Col(dcc.Upload(id=id_pangenome_upload,
                                                     multiple=False,
                                                     children=[
                                                         dbc.Row([dbc.Col(html.I(className="fas fa-seedling fa-2x"),
                                                                          className="col-md-2"),
                                                                  html.P(
                                                                      "Drag & drop pangenome.json file or select file..",
                                                                      className="col-md-10")])

                                                     ], className="file_upload"), width={"size": 4, "offset": 4})
                              ])

_task_parameters_row = dbc.Row(id=id_task_parameters_row,
                               children=html.Div([html.Div(html.H3("Task parameters"), className="panel-heading"),
                                                  dcc.Loading(
                                                      html.Div(id=id_task_parameters_vis, className="panel-body"),
                                                      type="circle")],
                                                 ),
                               className="vis_row")

_input_data_row = dbc.Row(style={'display': 'none'}, children=[
    dbc.Col(html.Div(id=id_input_dagmaf_vis,
                     children=[html.H3("MAF graph"),
                               dcc.Loading(cyto.Cytoscape(id=id_mafgraph_graph,
                                                          elements=[],
                                                          layout={'name': 'cose'},
                                                          autoRefreshLayout=True,
                                                          style={'width': 'auto',
                                                                 'height': '350px'},
                                                          zoom=1,
                                                          # style={'width': 'auto',
                                                          #        'height': '300px'},
                                                          stylesheet=mafgraph_component.get_mafgraph_stylesheet(),
                                                          # autolock=True,
                                                          boxSelectionEnabled=False,
                                                          # autoungrabify=True,
                                                          autounselectify=True),
                                           type="circle")]
                     ))])

_pangenome_row = dbc.Row(children=[dbc.Col(html.H4("Pangenome - Cut Width statistic"), width=12),
                                   dbc.Col([html.P("Representation of full poagraph as Cut Width statistics."),
                                            html.P("Cut Width - edges count between two consecutive columns."),
                                            html.I(id="arrow_icon",
                                                   className="fas fa-level-down-alt fa-flip-horizontal fa-5x")],
                                           width=2),
                                   dbc.Col(html.Div(id=id_full_pangenome_container,
                                                    style={'visibility': 'hidden'},
                                                    children=[dcc.Loading(dcc.Graph(
                                                        id=id_full_pangenome_graph,
                                                        # style={'width': 'auto'},
                                                        style={'height': '200px', 'width': 'auto'},
                                                        figure={},
                                                        config={
                                                            'displayModeBar': False,
                                                        }
                                                    ), type="circle")]), width=10)], className="vis_row")

_poagraph_row = dbc.Row(children=[dbc.Col(html.H4("Pangenome - a closer view on graph details"), width=12),
                                  dbc.Col([html.P(
                                      "This is a visualisation of pangenome internal representation as a PoaGraph"),
                                      html.Div(id=id_poagraph_node_info)], width=2),
                                  dbc.Col(html.Div(id=id_poagraph_container,
                                                   children=dcc.Loading(cyto.Cytoscape(id=id_poagraph,
                                                                                       layout={
                                                                                           'name': 'preset'},
                                                                                       stylesheet=poagraph_component.get_poagraph_stylesheet(),
                                                                                       elements=[
                                                                                       ],
                                                                                       style={'width': 'auto',
                                                                                              'height': '500px',
                                                                                              'background-color': 'white'},
                                                                                       zoom=20,
                                                                                       # minZoom=0.9,
                                                                                       # maxZoom=1.1,
                                                                                       # panningEnabled=False,
                                                                                       # userPanningEnabled=False,
                                                                                       boxSelectionEnabled=False,
                                                                                       # autoungrabify=True,
                                                                                       autolock=True,
                                                                                       autounselectify=True
                                                                                       ), type="circle")), width=10)],
                        className="vis_row")

_affinity_tree_row = dbc.Row(children=[dbc.Col([html.H4("Affinity Tree")], width=12),
                                       dbc.Col([html.P(
                                           "This is affinity tree generated using this software. It is similar to a phylogenetic tree but every node has a consensus sequence assigned.")],
                                           width=2),
                                       dbc.Col([dcc.Graph(
                                           id=id_consensus_tree_graph,
                                           style={'height': '600px', 'width': 'auto'},
                                           config={
                                               'displayModeBar': True
                                           },

                                           # style={'width': 'auto'}
                                       ),
                                           html.Div(dcc.Slider(
                                               id=id_consensus_tree_slider,
                                               min=0,
                                               max=1,
                                               marks={
                                                   int(i) if i % 1 == 0 else i: '{}'.format(i)
                                                   for i
                                                   in
                                                   [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8,
                                                    0.9,
                                                    1]},
                                               step=0.01,
                                               value=0.5,
                                               dots=True
                                           ), style={"margin": '-1% 20% 0% 3%'})], width=7, id="consensus_tree_col"),
                                       dbc.Col(children=[html.H5("Metadata in affinity tree leaves:"),
                                                         dcc.Dropdown(
                                                             id=id_leaf_info_dropdown,
                                                             style={'margin-bottom': '20px'},
                                                             options=[
                                                             ],
                                                             value='SEQID'
                                                         ),
                                                         html.H5(["Affinity tree node details:", html.P(
                                                             id=id_consensus_node_details_header
                                                         ), ]),

                                                         html.Img(
                                                             id=id_consensus_node_details_distribution,
                                                             style={'max-width': '100%', 'margin-bottom': '2%'}
                                                         ),
                                                         dcc.Loading(dash_table.DataTable(
                                                             id=id_consensus_node_details_table,
                                                             style_table={
                                                                 'maxHeight': '800',
                                                                 'overflowY': 'scroll'
                                                             },
                                                             style_cell={'textAlign': 'left'},
                                                             sorting=True
                                                         ), type="circle")], width=3)], className="vis_row")

_consensus_table_row = dbc.Row(children=[dbc.Col(html.H4("Consensuses on current cut level"), width=12),
                                         dbc.Col(html.Div(id=id_consensus_table_container,
                                                          children=dcc.Loading(
                                                              dash_table.DataTable(id=id_consensuses_table,
                                                                                   sorting=True,
                                                                                   sorting_type="multi"),
                                                              type="circle")), width=12,
                                                 style={'overflow-x': 'scroll'})], className="vis_row")

loading_style = "circle"
_pangviz_tab_content = dbc.Container([
    dcc.Store(id=id_visualisation_session_info, data=""),
    dcc.Store(id=id_elements_cache_info, data=""),
    dbc.Row(style={'display': 'none'}, children=[html.Div(id=id_pangenome_hidden),
                                                 html.Div(id=id_poagraph_hidden),
                                                 html.Div(id=id_full_consensustree_hidden),
                                                 html.Div(id=id_partial_consensustable_hidden),
                                                 html.Div(id=id_current_consensustree_hidden),
                                                 html.Div(id=id_full_consensustable_hidden),
                                                 html.Div(id=id_consensus_node_details_table_hidden)]),
    _load_pangenome_row,
    dbc.Collapse(
        id=id_pangviz_result_collapse,
        children=[_task_parameters_row,
                  _input_data_row,
                  _pangenome_row,
                  _poagraph_row,
                  _affinity_tree_row,
                  _consensus_table_row])
], fluid=True)


def get_task_description_layout(jsonpangenome: PangenomeJSON) -> dbc.CardDeck():
    fasta_provider_paragraph = html.P()
    if jsonpangenome.task_parameters.multialignment_format == "Maf":
        opt = jsonpangenome.task_parameters.fasta_complementation_option
        if opt == "ConstSymbolProvider":
            o = f"Const symbol {jsonpangenome.task_parameters.missing_base_symbol}"
        elif opt == "FromFile":
            o = f"Fasta file {jsonpangenome.task_parameters.fasta_source_file}"
        else:
            o = "NCBI"
        fasta_provider_paragraph = html.P(f"Fasta provider: {o}")

    if jsonpangenome.task_parameters.consensus_type == "poa":
        cons_type_paragraph = [html.P(f"Hbmin: {jsonpangenome.task_parameters.hbmin}")]
    else:
        cons_type_paragraph = [html.P(f"P: {jsonpangenome.task_parameters.p}"),
                               html.P(f"Stop: {jsonpangenome.task_parameters.stop}")]

    return dbc.CardDeck(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.CardText([
                                html.P(f"Multialignment: {jsonpangenome.task_parameters.multialignment_file_path}"),
                                html.P(f"Metadata : {jsonpangenome.task_parameters.metadata_file_path}"),
                                fasta_provider_paragraph
                            ]
                            ),
                        ]
                    ),
                    dbc.CardFooter("PoaGraph Configuration", className="text-center"),
                ],
                outline=True,
                color="dark",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.CardText([
                                             html.P(f"Algorithm: {jsonpangenome.task_parameters.consensus_type}"),
                                             html.P(f"Blosum file: {jsonpangenome.task_parameters.blosum_file_path}")]
                                         + cons_type_paragraph

                                         ),
                        ]
                    ),
                    dbc.CardFooter("Consensus Configuration", className="text-center"),
                ],
                outline=True,
                color="dark",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.CardText([
                                html.P(f"Time: {jsonpangenome.task_parameters.running_time}"),
                                html.P(f"Poagraph nodes count: {len(jsonpangenome.nodes)}"),
                                html.P(f"Sequences count: {len(jsonpangenome.sequences)}"),
                                html.P(f"Consensuses count: {len(jsonpangenome.consensuses)}"),
                            ]
                            ),
                        ]
                    ),
                    dbc.CardFooter("Processing info", className="text-center"),
                ],
                outline=True,
                color="dark",
            ),
        ]
    )
