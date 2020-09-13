import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
from pangtreebuild.serialization.json import PangenomeJSON

from dash_app.layout import links

"""--------------------------------FAQ---------------------------------------"""

def contact_card(name, email_address):
    return dbc.Card([dbc.CardBody([
        html.H5(name, className="card-title text-info"),
        html.P(email_address, className='card-text')
    ])], outline=True, color="info")

def get_answer(question, answer, extra=[]):
    return html.Details([
        html.Summary(question),
        html.Div([html.P(answer)]+extra, className="answer"),
    ], className="question-answer")

def faq():
    pangtreebuild_package = [
        html.Span([
            "The underlying software is available at ",
            links.blank_link("GitHub", href=links.pangtreebuild_link),
            ". It can be incorporated into your Python application in this simple way:"
        ]),
        html.Div(dcc.Markdown(links.package_card_text), className="code_markdown"),
        html.Span("or used as a CLI tool:"),
        html.Div(dcc.Markdown('''
            pangtreebuild --multialignment "example.maf" --fasta_provider "file" 
            --fasta_path "example.fasta" --affinity tree'''),
            className="code_markdown"
        )
    ]

    return html.Div([
        get_answer(
            "Do I need GUI to use PangTreeBuild?", 
            "No, PangTreeBuild is a standalone Python library.",
            pangtreebuild_package,
        ),
        html.Div([
            "If you have any questions, please contact us at dojer@mimuw.edu.pl or "
            "paulina.knut@gmail.com.",
            # contact_card("Norbert Dojer", "dojer@mimuw.edu.pl"),
            # contact_card("Paulina Knut", "paulina.knut@gmail.com"),
        ],
        className='footer'),
        
    ], className="container")


"""-------------------------------INDEX--------------------------------------"""


def index_info_card(header, fa_icon, info):
    return dbc.Card([
        dbc.CardHeader(
            dbc.Row([
                dbc.Col(html.I(className=f"fas {fa_icon} fa-2x"), className="col-md-3 my-auto"),
                html.P(header, className="col-md-9 my-auto")
            ])
        ),
        dbc.CardBody([html.P(info, className='card-text')]),
    ])


def logo_col(logo_href, img_src, img_class, title, text):
    return dbc.Col([
        html.A(
            href=logo_href,
            children=html.Div(
                html.Img(className=img_class, src=img_src),
                className="tools-logo circle-img"
            )
        ),
        html.Div([html.H4(title), html.P(text)]),
    ], className='tools-logo')


def index():
    tools_logos = dbc.Row([
        logo_col(
            logo_href="/pangtreebuild",
            img_src=links.build_logo_src,
            img_class="small_icon",
            title="PangTreeBuild",
            text="tool for multiple sequence alignment analysis."
        ),
        logo_col(
            logo_href="/pangtreevis",
            img_src=links.vis_logo_src,
            img_class="medium_icon",
            title="PangTreeVis",
            text="visualises the results in browser."
        ),
    ])
    credits_footer = html.Div([
        "PangTreeBuild and PangTreeVis icons made by ",
        links.blank_link("Freepik", href=links.freepik_link),
        " from ",
        links.blank_link("www.flaticon.com", href=links.flaticon_link)
    ], 
    className="footer")

    return html.Div([
        tools_logos,
        dbc.Row(dbc.CardDeck([
            index_info_card(
                header="Build graph representation of multiple sequence alignment",
                fa_icon="fa-bezier-curve",
                info=html.Ul([
                    html.Li(["Input formats: ", links.maf_info, ", ", links.po_info]),
                    html.Li(["Internal representation: ", links.pograph_info]),
                    html.Li(["Cycles in graph removed with ", links.mafgraph_info]),
                    html.Li("Complement missing parts from NCBI or fasta")
                ])
            ),
            index_info_card(
                header="Find sequences consensus",
                fa_icon="fa-grip-lines",
                info=[
                    "This tool extends Partial Order Alignment (POA) algorithm introduced by ",
                    links.blank_link("Lee et al.", href=links.pograph_info_link),
                    ". It provides:",
                    html.Ul([
                        html.Li([
                            html.Strong("Consensuses"),
                            " - agreed representations of input subsets"
                        ]),
                        html.Li([
                            html.Strong("Consensus Tree"),
                            " - a structure similar to phylogenetic tree but it has "
                            "a consensus assigned to every node"]),
                        html.Li([
                            html.Strong("Compatibility"),
                            " - a measure of similarity between sequence and consensus"])
                    ])
                ]
            ),
            index_info_card(
                header="Visualise results",
                fa_icon="fa-eye",
                info=html.Ul([
                    html.Li("MAF blocks graph"),
                    html.Li("Multiple sequence alignment as Partial Order Graph"),
                    html.Li("Consensus tree"),
                    html.Li("Compatibilities relations")
                ])
            )
        ])),
        html.Br(),
        credits_footer
    ], className="container")


"""-------------------------------TOOLS--------------------------------------"""


def pangtreebuild():
    return _poapangenome_tab_content


def pangtreevis():
    return _pangviz_tab_content


"""-------------------------- PANGTREEBUILD ---------------------------------"""

def pang_task_form(label, label_id, form, text, extra_label_id=None):
    form_children = [
        html.Div([
            html.H5(label), 
            html.Div(text, className="secondary")
            ], className="center_flex_form width40"),
        html.Div(form, className="center_flex_form width40")
    ]
    if extra_label_id:
        form_children.append(
            dbc.Label(id=extra_label_id, width=2, className="poapangenome_label center_flex_form")
        )
    return html.Div(form_children, className="pang_form")


_data_type_form = pang_task_form(
    label_id="data_type",
    label="Data Type",
    form=[
        dbc.RadioItems(
            value="Nucleotides",
            id="data_type",
            options=[{"label": l, "value": v}
                     for l, v in [("Nucleotides", "Nucleotides"), ("Proteins", "Aminoacids")]])
    ],
    text="Type of aligned sequences provided in the uploaded multialignment sfile."
)

_metadata_upload_form = pang_task_form(
    label_id="metadata_upload",
    label="Sequences metadata",
    extra_label_id="metadata_upload_state_info",
    form=[
        dcc.Upload(id="metadata_upload", multiple=False, children=[
            dbc.Row([
                dbc.Col(html.I(className="fas fa-file-csv fa-2x"), className="col-md-2"),
                html.P("Drag & drop or select file...", className="col-md-10")
            ])
        ], className="file_upload"),
        dcc.Store(id="metadata_upload_state")
    ],
    text=[links.metadata_upload_form_text, links.metadata_example_info],
)

_multialignment_upload_form = pang_task_form(
    label_id="multialignment_upload",
    label="Multialignment",
    extra_label_id="multialignment_upload_state_info",
    form=[
        dcc.Upload(
            id="multialignment_upload",
            multiple=False,
            children=[
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-align-justify fa-2x"), className="col-md-2"),
                    html.P("Drag & drop or select file...", className="col-md-10")
                ])
            ], className="file_upload"),
        dcc.Store(id="multialignment_upload_state"),
    ],
    text=[
        "Accepted formats: ",
        links.maf_info,
        ", ",
        links.po_info,
        ". See example file: ",
        links.maf_example_link
    ],
)

_missing_data_form = dbc.Collapse([
    pang_task_form(
        label_id="fasta_provider_choice",
        label="Missing nucleotides source",
        form=[
            dbc.RadioItems(
                value="NCBI",
                options=[{"label": l, "value": v} for l, v in
                         [("NCBI", "NCBI"), ("Fasta File", "File"), ("Custom symbol", "Symbol")]],
                id="fasta_provider_choice")],
        text="MAF file may not inlcude full sequences. "
             "Specify source of missing nucleotides/proteins."
    ),
    dbc.Collapse(
        id="missing_symbol_param",
        children=pang_task_form(
            label_id="fasta_provider_choice",
            label="Missing symbol for unknown nucleotides/proteins",
            form=[
                dbc.Input(value="?",
                          id="missing_symbol_input",
                          type='text',
                          maxLength=1,
                          minLength=1)],
            text="Any single character is accepted but it must be present in "
                 "BLOSUM file. Default BLOSUM file uses '?'."
        )
    ),
    dbc.Collapse(
        id="fasta_upload_param",
        children=pang_task_form(
            label_id="fasta_provider_choice",
            label="Missing symbols file source",
            extra_label_id="fasta_upload_state_info",
            form=[
                dcc.Upload(
                    id="fasta_upload",
                    multiple=False,
                    children=[
                        dbc.Row([
                            dbc.Col(html.I(className="fas fa-align-left fa-2x"),
                                    className="col-md-2"),
                            html.P("Drag & drop or select file...", className="col-md-10")
                        ])
                    ], className="file_upload"),
                dcc.Store(id="fasta_upload_state")
            ],
            text="Provide zip with fasta files or single fasta file. It must contain full "
                 "sequences which are not fully represented in provided MAF file."
        )
    )
], id="maf_specific_params")

_consensus_algorithm_form = pang_task_form(
    label_id="data_type",
    label="Consensus algorithm",
    form=[
        dbc.RadioItems(
            value="tree",
            options=[{'label': "Poa", 'value': 'poa'}, {'label': 'Tree', 'value': 'tree'}],
            id="consensus_algorithm_choice")
    ],
    text=[
        "There are two available algorithms for consensus tree generation. 'Poa' by ",
        links.blank_link("Lee et al.", href=links.poa_alg_link),
        " and 'Tree' algorithm described ",
        links.blank_link("here", href=links.tree_alg_link)
    ]
)

_poa_hbmin_form = dbc.Collapse(
    pang_task_form(
        label_id="hbmin_input",
        label="HBMIN",
        form=[dbc.Input(value=0.9, type='number', min=0, max=1, id="hbmin_input")],
        text="HBMIN is required minimum value of similarity between sequence and "
             "assigned consensus. It must be a value from range [0,1]."
    ),
    id="poa_specific_params"
)

_tree_params_form = dbc.Collapse([
    pang_task_form(
        label_id="hbmin_input",
        label="P",
        form=[dbc.Input(value=1, type='number', min=0, id="p_input")],
        text=[
            "P is used during cutoff search. P < 1 decreases distances between small "
            "compatibilities and increases distances between the bigger ones while P > 1 "
            "works in the opposite way. This value must be > 0. ",
            links.blank_link("Read more...", href=links.pangtreebuild_link)
        ]
    ),
    pang_task_form(
        label_id="hbmin_input",
        label="Stop",
        form=[dbc.Input(value=1, type='number', min=0, max=1, id="stop_input")],
        text="Minimum value of compatibility in tree leaves. It must be a value from range [0,1]."
    )],
    id="tree_specific_params"
)

_output_form = pang_task_form(
    label_id="label_output_configuration",
    label="Additional output options",
    form=[
        dbc.Checklist(
            id="output_configuration",
            options=[
                {'label': 'Create FASTA (all sequences and consensuses in fasta format)',
                 'value': 'fasta'},
                {'label': 'Create PO (poagraph in PO format)', 'value': 'po'},
                {'label': 'Create NEWICK (Affinity Tree in newick format)', 'value': 'newick'},
                # {'label': 'Include nodes ids in pangenome.json (greatly increases file size)',
                #  'value': 'nodes'}, 
            ],
            value=['fasta', 'po'])],
    text=""
)

_example_input = html.Div([
    html.H5("Example Input Data"),
    html.Div([
        html.H6("Ebola"),
        dbc.Button("Use Ebola data", id="use-ebola-button"),
        html.Div([
            "This dataset orginates from ",
            links.blank_link("UCSC Ebola Portal", href="https://genome.ucsc.edu/ebolaPortal/"),
            '. Generating results takes several minutes. Be patient :)',
            html.Br(),
            links.blank_link("See example file...", href=links.ebola_data_link),
        ], className="secondary"),   
    ], className="center_flex_form example"),
    html.Div([
        html.H6("Ebola subset"),
        dbc.Button("Use Ebola subset data", id="use-ebola_subset-button"),
        html.Div([
            "This multialignment contains a subset - only one block - of the original multialignment.", 
            html.Br(),
            links.blank_link("Read more...", href=links.ebola_subset_link),
        ], className="secondary"),   
    ], className="center_flex_form example"),
    html.Div([
        html.H6("Toy example"),
        dbc.Button("Use Toy data", id="use-toy-button",),
        html.Div([
            "This is a toy example of small multialignment in MAF format, CSV metadata and "
            "FASTA for missing nucleotides.",
            html.Br(),
            links.blank_link("See example files...", href=links.toy_data_link)
        ], className="secondary"),
    ], className="center_flex_form example")
], className="pang_form")

_poapangenome_form = dbc.Form([
    _example_input,
    _data_type_form,
    _metadata_upload_form,
    _multialignment_upload_form,
    _missing_data_form,
    _consensus_algorithm_form,
    _poa_hbmin_form,
    _tree_params_form,
    _output_form
])

_poapangenome_tab_content = html.Div([
    dcc.ConfirmDialog(
        id='confirm_run',
        message='The results are ready, scroll down.',
    ),
    dcc.Store(id="session_state"),
    dcc.Store(id="session_dir"),
    dbc.Row([
        html.Div([
            html.H3("Task Parameters"),
            _poapangenome_form,
            dbc.Row([
                dbc.Col(
                    dbc.Button(
                        "Run",
                        id="pang_button",
                        # color="primary",
                        className="offset-md-5 col-md-4 "
                    ),
                ),
                dbc.Col(
                    dcc.Loading(
                        id="l2",
                        children=html.Div(id="running_indicator"),
                        type="default")
                )
            ])
        ], id='poapangenome_form'),
    ], className="poapangenome_content"),
    dbc.Collapse(
        html.Div([
            dbc.Row([
                html.I(id="result_icon"),
                html.H3("Task completed!", className="next_to_icon"),
                html.A(
                    dbc.Button(
                        "Download result files",
                        # block=True,
                        className="result_btn",
                        color="info"
                    ),
                    id="download_processing_result"
                )
            ]),
            html.Div(id="poapangenome_result_description"),
        ]), 
        id="poapangenome_result")
])

"""--------------------------- PANGTREEVIS ----------------------------------"""

_load_pangenome_row = dbc.Row(
    id="pangviz_load_row",
    children=[
        dcc.Upload(
            id="pangenome_upload",
            multiple=False,
            children=[
                html.I(className="fas fa-seedling fa-2x upload-icon"),
                "Drag & drop pangenome.json file or select file.."
            ], className="file_upload"
        ),
    ])

_task_parameters_row = dbc.Row(
    id="task_parameters_row",
    className="vis_row",
    children=html.Details([
        html.Summary('Task parameters'),
        dcc.Loading(
            type="circle",
            children=html.Div(id="task_parameters_vis", className="panel-body")
        )
    ])
)


_pangenome_row = html.Div(
    children=[
        html.H4("Poagraph\n"),
        # html.P("Representation of full poagraph as gap statistics."),
        html.P("Drag the green rectangle to see details of the highlighted pangenome region."),
        html.Div(
            id="full_pangenome_container",
            # style={'width': '100%'},
            children=[
                dcc.Loading(
                    dcc.Graph(
                        id="full_pangenome_graph",
                        figure={},
                        config={
                            'displayModeBar': False,
                            'edits': {'shapePosition': True}
                        },
                    ), 
                    type="circle"
                )
            ]
        )
    ]
)

_poagraph_row = dbc.Row(
    children=[
        html.Details([
            html.Summary('Pangenome'),
            _pangenome_row,
            html.Div([
                # html.H4("Pangenome - a closer view on graph details\n"),
                # html.P("This is a visualisation of pangenome internal "
                #        "representation as a PoaGraph"),
                html.Div(id="poagraph_node_info"),
                html.Div(
                    id="poagraph_container",
                    style={'width': '100%', 'text-align': 'center'},
                    children=dcc.Graph(
                        id="poagraph",
                        figure={},
                        config={
                            'displayModeBar': False,
                            'staticPlot': True
                        }
                    )
                ),
                html.P("Highlight the sequence:"),
                dcc.Dropdown(
                    id="poagraph_dropdown",
                    options=[
                        {'label': f'seq{i}', 'value': f'seq{i}'} for i in range(1, 5)
                    ],
                    value='',
                    multi=False,
                ) 
            ])
        ])
    ], className="vis_row")

_consensus_table = html.Div([
    html.H4("Consensuses on current cut level"),
    html.Div(
        dcc.Loading(
            dash_table.DataTable(
                id="consensuses_table",
                sort_action="native",
                sort_mode="multi",
                data=[{"ID": 0}, {"ID": 1}],
                columns=[{"name": i, "id": i} for i in ["ID"]]
            ),
            type="circle"),
        id="consensus_table_container",
        style={'overflow-x': 'scroll'})
    ])

_affinity_tree_row = html.Div([
    html.Details([
        html.Summary('Affinity Tree'),
        html.P(
            "This is affinity tree generated using this software. It is similar to "
            "a phylogenetic tree but every node has a consensus sequence assigned."
        , style={"text-align": "left"}),
        html.Div([
            html.H5("Metadata in affinity tree leaves:"),
            dcc.Dropdown(
                id="leaf_info_dropdown",
                style={'margin-bottom': '20px'},
                options=[],
                value='SEQID'
            )], 
            style={'width': '20%'}),
        dcc.Loading(
            dcc.Graph(
                id="consensus_tree_graph",
                style={'height': '600px', 'width': 'auto'},
                config={
                    'displayModeBar': False,
                    'scrollZoom': False,
                },
            ),
            type="circle"
        ),
        dcc.Slider(
            id="consensus_tree_slider",
            min=0,
            max=1,
            marks={i / 10: str(i / 10) for i in range(11)},
            step=0.01,
            value=0.5,
            dots=True
        ),

        # html.H5([
        #     "Affinity tree node details:",
        #     html.P(id="consensus_node_details_header")
        # ]),
        # html.Img(
        #     id="consensus_node_details_distribution",
        #     style={'max-width': '100%', 'margin-bottom': '2%'}
        # ),
        # dcc.Loading(dash_table.DataTable(
        #     id="consensus_node_details_table",
        #     style_table={'maxHeight': '800', 'overflowY': 'scroll'},
        #     style_cell={'textAlign': 'left'},
        #     sort_action='native'
        # ), type="circle"),
        html.Br(),
        _consensus_table
        ], className="vis_row")
    ])

loading_style = "circle"
_pangviz_tab_content = dbc.Container([
    dcc.Store(id="visualisation_session_info", data=""),
    dcc.Store(id="elements_cache_info", data=""),
    dbc.Row(
        style={'display': 'none'},
        children=[
            html.Div(id="pangenome_hidden"),
            html.Div(id="poagraph_hidden"),
            html.Div(id="full_consensustree_hidden"),
            html.Div(id="partial_consensustable_hidden"),
            html.Div(id="current_consensustree_hidden"),
            html.Div(id="full_consensustable_hidden"),
            # html.Div(id="consensus_node_details_table_hidden")
        ]
    ),
    _load_pangenome_row,
    dbc.Collapse(
        id="pangviz_result_collapse",
        children=[
            _task_parameters_row,
            _poagraph_row,
            _affinity_tree_row,
        ])
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
        cons_type_paragraph = [
            html.P(f"Hbmin: {jsonpangenome.task_parameters.hbmin}")]
    else:
        cons_type_paragraph = [html.P(f"P: {jsonpangenome.task_parameters.p}"),
                               html.P(
                                   f"Stop: {jsonpangenome.task_parameters.stop}")]

    return dbc.CardDeck([
        dbc.Card([
            dbc.CardBody([
                html.P([
                    html.P(
                        f"Multialignment: {jsonpangenome.task_parameters.multialignment_file_path}"),
                    html.P(
                        f"Metadata : {jsonpangenome.task_parameters.metadata_file_path}"),
                    fasta_provider_paragraph
                ], className='card-text'),
            ]),
            dbc.CardFooter("PoaGraph Configuration", className="text-center"),
        ], outline=True, color="dark"),
        dbc.Card([
            dbc.CardBody([
                html.P([
                           html.P(
                               f"Algorithm: {jsonpangenome.task_parameters.consensus_type}"),
                           html.P(
                               f"Blosum file: {jsonpangenome.task_parameters.blosum_file_path}")
                       ] + cons_type_paragraph, className='card-text'),
            ]),
            dbc.CardFooter("Consensus Configuration", className="text-center")
        ], outline=True, color="dark"),
        dbc.Card([
            dbc.CardBody([
                html.P([
                    html.P(
                        f"Time: {jsonpangenome.task_parameters.running_time}"),
                    html.P(["Poagraph nodes count: ",
                            f"{len(jsonpangenome.nodes)}" if jsonpangenome.nodes else "unknown"]),
                    html.P(f"Sequences count: {len(jsonpangenome.sequences)}"),
                    html.P(
                        f"Consensuses count: {len(jsonpangenome.affinitytree)}"),
                ], className='card-text'),
            ]),
            dbc.CardFooter("Processing info", className="text-center")
        ], outline=True, color="dark"),
    ])
