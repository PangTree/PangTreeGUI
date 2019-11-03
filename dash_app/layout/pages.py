import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from pangtreebuild.output.PangenomeJSON import PangenomeJSON

from .layout_ids import *
import dash_cytoscape as cyto
import dash_table
from ..components import mafgraph as mafgraph_component
from ..components import poagraph as poagraph_component

"""------------------------------CONTACT-------------------------------------"""


def contact_card(name, email_address):
    return dbc.Card([dbc.CardBody([
        html.H5(name, className="card-title text-info"),
        html.P(email_address, className='card-text')
    ])], outline=True, color="info")


def contact():
    return dbc.Container([
        contact_card("Norbert Dojer, PhD.", "dojer@mimuw.edu.pl"),
        contact_card("Paulina Dziadkiewicz, M.Sc.", "pedziadkiewicz@gmail.com"),
        contact_card("Paulina Knut, B.Sc.", "paulina.knut@gmail.com"),
    ])


"""-------------------------------INDEX--------------------------------------"""


def index_info_card(header, fa_icon, info):
    return dbc.Card([
        dbc.CardHeader(dbc.Row([
            dbc.Col(html.I(className=f"fas {fa_icon} fa-2x"),
                    className="col-md-3 my-auto"),
            html.P(header, className="col-md-9 my-auto")
        ])),
        dbc.CardBody([html.P(info, className='card-text')]),
    ])


def index():
    build_logo_src = "https://s3.amazonaws.com/media-p.slid.es/uploads/" \
                     "1047434/images/6497196/pasted-from-clipboard.png"
    vis_logo_src = "https://s3.amazonaws.com/media-p.slid.es/uploads/" \
                   "1047434/images/6497198/pasted-from-clipboard.png"
    tools_logos = dbc.Row([
        dbc.Col([
            html.A(href="/pangtreebuild",
                   children=html.Img(
                       className="tools-logo circle-img",
                       src=build_logo_src)),
            html.Div([
                html.H4('PangTreeBuild'),
                html.P("tool for multiple sequence alignment analysis.")
            ], style={"line-height": "40px"}),
        ], className='tools-logo'),
        dbc.Col([
            html.A(href="/pangtreevis",
                   children=html.Img(
                       className="tools-logo circle-img",
                       src=vis_logo_src)),
            html.Div([
                html.H4('PangTreeVis'),
                html.P("visualises the results in browser.")
            ], style={"line-height": "40px"}),
        ], className='tools-logo')
    ])

    maf_info = html.A(
        "MAF",
        href="http://www1.bioinf.uni-leipzig.de/UCSC/FAQ/FAQformat.html"
             "#format5",
        target="_blank")
    po_info = html.A(
        "PO",
        href="https://github.com/meoke/pang/blob/master/README.md"
             "#po-file-format-specification",
        target="_blank")
    pograph_info = html.A(
        "Partial Order graph",
        href="https://doi.org/10.1093/bioinformatics/18.3.452",
        target="_blank")
    mgraph_info = html.A(
        "Mafgraph",
        href="https://github.com/anialisiecka/Mafgraph",
        target="_blank")

    return dbc.Container(
        html.Div([
            tools_logos,
            dbc.Row(dbc.CardDeck([
                index_info_card(
                    header="Build graph representation of multiple sequence "
                           "alignment",
                    fa_icon="fa-bezier-curve",
                    info=html.Ul([
                        html.Li(["Input formats: ", maf_info, ", ", po_info]),
                        html.Li(["Internal representation: ", pograph_info]),
                        html.Li(["Cycles in graph removed with ", mgraph_info]),
                        html.Li("Complement missing parts from NCBI or fasta")
                    ])
                ),
                index_info_card(
                    header="Find sequences consensus",
                    fa_icon="fa-grip-lines",
                    info=[
                        "This tool extends Partial Order Alignment (POA) "
                        "algorithm introduced by ",
                        html.A(
                            "Lee et al.",
                            href="https://doi.org/10.1093/bioinformatics/"
                                 "18.3.452",
                            target="_blank"),
                        ". It provides:",
                        html.Ul([
                            html.Li([
                                html.Strong("Consensuses"),
                                " - agreed representations of input subsets"]),
                            html.Li([
                                html.Strong("Consensus Tree"),
                                " - a structure similar to phylogenetic tree "
                                "but it has a consensus assigned to every "
                                "node"]),
                            html.Li([
                                html.Strong("Compatibility"),
                                " - a measure of similarity between sequence "
                                "and consensus"])
                        ])
                    ]
                ),
                index_info_card(
                    header="Visualise results",
                    fa_icon="fa-eye",
                    info=html.Ul([
                        html.Li("MAF blocks graph"),
                        html.Li("Multiple sequence alignment as "
                                "Partial Order Graph"),
                        html.Li("Consensus tree"),
                        html.Li("Compatibilities relations")
                    ])
                )
            ]))
        ])
    )


"""------------------------------PACKAGE-------------------------------------"""


def package():
    return dbc.Container([
        dbc.Row(
            html.Span([
                "The underlying software is available at ",
                html.A("GitHub",
                       href="https://github.com/meoke/pangtree",
                       target="_blank"),
                ". It can be incorporated into your Python application in this "
                "simple way:"
            ])
        ),
        dbc.Card(
            dbc.CardBody(
                dcc.Markdown('''
    from pangtreebuild import Poagraph, input_types, fasta_provider, consensus

    poagraph = Poagraph.build_from_dagmaf(
        input_types.Maf("example.maf"), 
        fasta_provider.FromNCBI()
    )
    affinity_tree = consensus.tree_generator.get_affinity_tree(
        poagraph,
        Blosum("BLOSUM80.mat"),
        output_dir,
        stop=1,
        p=1
    )
    pangenomejson = to_PangenomeJSON(poagraph, affinity_tree)
                ''')
            ),
            style={"margin": '30px 0px', 'padding': '10px'}),
        dbc.Row("or used as a CLI tool:"),
        dbc.Card(
            dbc.CardBody(
                dcc.Markdown('''
    pangtreebuild --multialignment "example.maf" --consensus tree --p 1 --stop 1
                ''')
            ),
            style={"margin": '30px 0px', 'padding': '10px'}),
        dbc.Row("Check out full documentation at the above link.")
    ])


"""-------------------------------TOOLS--------------------------------------"""


def pangtreebuild():
    return _poapangenome_tab_content


def pangtreevis():
    return _pangviz_tab_content


"""-------------------------- PANGTREEBUILD ---------------------------------"""


def pang_task_form(label, label_id, form, text, extra_label_id=None):
    form_group_children = [
        dbc.Label(label,
                  html_for=label_id,
                  width=3,
                  className="poapangenome_label"),
        dbc.Col(form + [dbc.FormText(text, color="secondary")], width=6)
    ]
    if extra_label_id:
        form_group_children.append(dbc.Label(
            id=extra_label_id,
            width=3,
            className="poapangenome_label"))

    return dbc.FormGroup(form_group_children, row=True)


_data_type_form = pang_task_form(
    label_id=id_data_type,
    label="Data Type",
    form=[
        dbc.RadioItems(value="Nucleotides",
                       id=id_data_type,
                       options=[{"label": l, "value": v}
                                for l, v in [("Nucleotides", "Nucleotides"),
                                             ("Proteins", "Aminoacids")]])
    ],
    text="Type of aligned sequences provided in the uploaded multialignment "
         "file."
)

_metadata_upload_form = pang_task_form(
    label_id=id_metadata_upload,
    label="Sequences metadata",
    extra_label_id=id_metadata_upload_state_info,
    form=[
        dcc.Upload(id=id_metadata_upload, multiple=False, children=[
            dbc.Row([
                dbc.Col(html.I(className="fas fa-file-csv fa-2x"),
                        className="col-md-2"),
                html.P("Drag & drop or select file...", className="col-md-10")
            ])
        ], className="file_upload"),
        dcc.Store(id=id_metadata_upload_state)
    ],
    text=[
        """CSV with sequences metadata. It will be included in the 
        visualisation. The 'seqid' column is obligatory and must match 
        sequences identifiers from MULTIALIGNMENT file. Other columns are 
        optional. Example file: """,
        html.A("metadata.csv",
               href="https://github.com/meoke/pang/blob/master/data/Fabricated/"
                    "f_metadata.csv",
               target="_blank")],
)

_multialignment_upload_form = pang_task_form(
    label_id=id_multialignment_upload,
    label="Multialignment",
    extra_label_id=id_multialignment_upload_state_info,
    form=[
        dcc.Upload(id=id_multialignment_upload, multiple=False, children=[
            dbc.Row([
                dbc.Col(html.I(className="fas fa-align-justify fa-2x"),
                        className="col-md-2"),
                html.P("Drag & drop or select file...", className="col-md-10")
            ])
        ], className="file_upload"),
        dcc.Store(id=id_multialignment_upload_state),
    ],
    text=[
        "Accepted formats: ",
        html.A(
            href="http://www1.bioinf.uni-leipzig.de/UCSC/FAQ/FAQformat.html"
                 "#format5",
            target="_blank",
            children="maf"),
        ", ",
        html.A(
            href="https://github.com/meoke/pang/blob/master/README.md"
                 "#po-file-format-specification",
            target="_blank",
            children="po"),
        ". See example file: ",
        html.A(
            href="https://github.com/meoke/pang/blob/master/data/Fabricated/"
                 "f.maf",
            target="_blank",
            children="example.maf")],
)

_missing_data_form = dbc.Collapse([
    pang_task_form(
        label_id=id_fasta_provider_choice,
        label="Missing nucleotides source",
        form=[
            dbc.RadioItems(
                value="NCBI",
                options=[{"label": l, "value": v} for l, v in
                         [("NCBI", "NCBI"), ("Fasta File", "File"),
                          ("Custom symbol", "Symbol")]],
                id=id_fasta_provider_choice)],
        text="MAF file may not inlcude full sequences. Specify source of "
             "missing nucleotides/proteins."
    ),
    dbc.Collapse(id=id_missing_symbol_param, children=pang_task_form(
        label_id=id_fasta_provider_choice,
        label="Missing symbol for unknown nucleotides/proteins",
        form=[
            dbc.Input(value="?",
                      id=id_missing_symbol_input,
                      type='text',
                      maxLength=1,
                      minLength=1)],
        text="Any single character is accepted but it must be present in "
             "BLOSUM file. Default BLOSUM file uses '?'."
    )),
    dbc.Collapse(id=id_fasta_upload_param, children=pang_task_form(
        label_id=id_fasta_provider_choice,
        label="Missing symbols file source",
        extra_label_id=id_fasta_upload_state_info,
        form=[
            dcc.Upload(
                id=id_fasta_upload,
                multiple=False,
                children=[
                    dbc.Row([
                        dbc.Col(html.I(className="fas fa-align-left fa-2x"),
                                className="col-md-2"),
                        html.P("Drag & drop or select file...",
                               className="col-md-10")
                    ])
                ], className="file_upload"),
            dcc.Store(id=id_fasta_upload_state)
        ],
        text="Provide zip with fasta files or single fasta file. It must "
             "contain full sequeneces which are not fully represented in "
             "provided MAF file."
    ))
], id=id_maf_specific_params)

_consensus_algorithm_form = pang_task_form(
    label_id=id_data_type,
    label="Consensus algorithm",
    form=[
        dbc.RadioItems(value="tree",
                       options=[{'label': "Poa", 'value': 'poa'},
                                {'label': 'Tree', 'value': 'tree'}],
                       id=id_consensus_algorithm_choice)
    ],
    text=[
        "There are two available algorithms for consensus tree generation. "
        "'Poa' by ",
        html.A("Lee et al.",
               target="_blank",
               href="https://doi.org/10.1093/bioinformatics/btg109"),
        " and 'Tree' algorithm described ",
        html.A("here",
               target="_blank",
               href="https://github.com/meoke/pang"
                    "#idea-and-algorithm-description")
    ]
)

_blosum_upload_form = pang_task_form(
    label_id=id_blosum_upload,
    label="BLOSUM",
    extra_label_id=id_blosum_upload_state_info,
    form=[
        dcc.Upload(id=id_blosum_upload,
                   multiple=False,
                   children=[dbc.Row([
                       dbc.Col(html.I(className="fas fa-table fa-2x"),
                               className="col-md-2"),
                       html.P("Drag & drop or select file...",
                              className="col-md-10")])],
                   className="file_upload"),
        dcc.Store(id=id_blosum_upload_state)
    ],
    text=[
        "This parameter is optional as default BLOSUM file is ",
        html.A(
            href="https://github.com/meoke/pang/blob/master/bin/blosum80.mat",
            target="_blank",
            children="BLOSUM80"),
        ". The BLOSUM matrix must contain '?' or the custom symbol for "
        "missing nucleotides, if specified."
    ]
)

_poa_hbmin_form = dbc.Collapse(pang_task_form(
    label_id=id_hbmin_input,
    label="HBMIN",
    form=[dbc.Input(value=0.9, type='number', min=0, max=1, id=id_hbmin_input)],
    text="HBMIN is required minimum value of similarity between sequence and "
         "assigned consensus. It must be a value from range [0,1]."
), id=id_poa_specific_params)

_tree_params_form = dbc.Collapse([
    pang_task_form(
        label_id=id_hbmin_input,
        label="P",
        form=[dbc.Input(value=1, type='number', min=0, id=id_p_input)],
        text=[
            "P is used during cutoff search. P < 1 decreases distances "
            "between small compatibilities and increases distances between "
            "the bigger ones while P > 1 works in the opposite way. "
            "This value must be > 0. ",
            html.A("Read more...",
                   href="https://github.com/meoke/pang",
                   target="_blank")
        ]
    ),
    pang_task_form(
        label_id=id_hbmin_input,
        label="Stop",
        form=[
            dbc.Input(value=1, type='number', min=0, max=1, id=id_stop_input)
        ],
        text="Minimum value of compatibility in tree leaves. It must be "
             "a value from range [0,1]."
    )
], id=id_tree_specific_params)

_output_form = pang_task_form(
    label_id=id_output_configuration,
    label="Additional output generation",
    form=[
        dbc.Checklist(
            id=id_output_configuration,
            options=[{
                'label': 'FASTA (all sequences and consensuses in fasta format)',
                'value': 'fasta'},
                {'label': 'PO (poagraph in PO format)',
                 'value': 'po'}],
            values=['fasta', 'po'])],
    text=""
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
        dbc.Col([
            html.H3("Task Parameters"),
            _poapangenome_form,
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Run",
                        id=id_pang_button,
                        color="primary",
                        className="offset-md-5 col-md-4 ")),
                dbc.Col(
                    dcc.Loading(
                        id="l2",
                        children=html.Div(id=id_running_indicator),
                        type="default")))
        ], className="col-md-7 offset-md-1", id='poapangenome_form'),
        dbc.Col([
            html.H3("Example Input Data"),
            dbc.Card([
                dbc.CardHeader(
                    dbc.Button(
                        "Ebola",
                        id="collapse-ebola-button",
                        className="mb-3 btn-block my-auto opac-button")),
                dbc.Collapse(
                    id="ebola_collapse",
                    children=dbc.CardBody([
                        html.P([
                            "This dataset orginates from ",
                            html.A("UCSC Ebola Portal",
                                   href="https://genome.ucsc.edu/ebolaPortal/",
                                   target="_blank")
                        ], className='card-text'),
                        html.P([
                            html.A(
                                href="https://github.com/meoke/pangtree/blob/"
                                     "master/data/Ebola/multialignment.maf",
                                target="_blank",
                                children="See example file...")
                        ], className='card-text'),
                    ]))
            ]),
        ], className="col-md-3 offset-md-1")
    ], className="poapangenome_content"),
    dbc.Collapse(
        id=id_poapangenome_result,
        children=dbc.Row(children=[
            dbc.Col([
                dbc.Row([
                    html.I(id=id_result_icon),
                    html.H3("Task completed!", className="next_to_icon")]),
                dbc.Col(html.Div(id=id_poapangenome_result_description),
                        className="col-md-11")
            ], className="col-md-6 offset-md-1"),
            dbc.Col([
                html.A(
                    dbc.Button("Download result files", block=True,
                               className="result_btn", color="info"),
                    id=id_download_processing_result),
                dbc.Button(
                    "Go to visualisation",
                    id=id_go_to_vis_tab,
                    n_clicks_timestamp=0,
                    block=True,
                    className="result_btn",
                    color="success",
                    style={"visibility": "hidden"})
            ], className="col-md-3 offset-md-1")]

        ))
])

"""--------------------------- PANGTREEVIS ----------------------------------"""

_load_pangenome_row = dbc.Row(
    id=id_pangviz_load_row,
    children=[
        dbc.Col(
            dcc.Upload(
                id=id_pangenome_upload,
                multiple=False,
                children=[
                    dbc.Row([
                        dbc.Col(
                            html.I(className="fas fa-seedling fa-2x"),
                            className="col-md-2"),
                        html.P(
                            "Drag & drop pangenome.json file or select file..",
                            className="col-md-10")
                    ])
                ], className="file_upload"), width={"size": 6, "offset": 3})
    ])

_task_parameters_row = dbc.Row(
    id=id_task_parameters_row,
    className="vis_row",
    children=html.Details([
        html.Summary(
            'Task parameters',
            style={'text-align': 'left'}),
        dcc.Loading(
            type="circle",
            children=html.Div(
                id=id_task_parameters_vis,
                className="panel-body"))
    ], style={'width': '100%'})
)

_input_data_row = dbc.Row(
    style={'display': 'none'},
    children=[
        dbc.Col(
            html.Div(
                id=id_input_dagmaf_vis,
                children=[
                    html.H3("MAF graph"),
                    dcc.Loading(
                        cyto.Cytoscape(
                            id=id_mafgraph_graph,
                            elements=[],
                            layout={'name': 'cose'},
                            autoRefreshLayout=True,
                            style={'width': 'auto', 'height': '350px'},
                            zoom=1,
                            stylesheet=mafgraph_component.get_mafgraph_stylesheet(),
                            boxSelectionEnabled=False,
                            autounselectify=True),
                        type="circle")]
            ))
    ])

_pangenome_row = html.Div(
    children=[
        html.H4("Pangenome - Cut Width statistic\n"),
        html.P("Representation of full poagraph as Cut Width statistics."),
        html.P("Cut Width - edges count between two consecutive columns."),
        html.Div(
            id=id_full_pangenome_container,
            style={'visibility': 'hidden', 'width': '100%'},
            children=[
                dcc.Loading(
                    dcc.Graph(
                        id=id_full_pangenome_graph,
                        style={'height': '250px', 'width': '100%'},
                        figure={},
                        config={'displayModeBar': False}
                    ), type="circle")]
        )
    ]
)

_poagraph_row = dbc.Row(
    children=[
        html.Details([
            html.Summary('Pangenome', style={'text-align': 'left'}),
            _pangenome_row,
            html.Div([
                html.H4("Pangenome - a closer view on graph details\n"),
                html.P("This is a visualisation of pangenome internal "
                       "representation as a PoaGraph"),
                html.Div(id=id_poagraph_node_info),
                html.Div(
                    id=id_poagraph_container,
                    style={'width': '100%', 'text-align': 'center'},
                    children=dcc.Loading(cyto.Cytoscape(
                        id=id_poagraph,
                        layout={'name': 'preset'},
                        stylesheet=poagraph_component.get_poagraph_stylesheet(),
                        elements=[],
                        style={'height': '500px', 'background-color': 'white'},
                        minZoom=0.9,
                        maxZoom=3,
                    ), type="circle"),
                )
            ])
        ], style={'width': '100%'})
    ], className="vis_row")

_affinity_tree_row = dbc.Row(
    children=[
        dbc.Col([html.H4("Affinity Tree")], width=12),
        dbc.Col(html.P("This is affinity tree generated using this software. "
                       "It is similar to a phylogenetic tree but every node "
                       "has a consensus sequence assigned."),
                width=2),
        dbc.Col([
            dcc.Graph(
                id=id_consensus_tree_graph,
                style={'height': '600px', 'width': 'auto'},
                config={'displayModeBar': True},
            ),
            html.Div(
                dcc.Slider(
                    id=id_consensus_tree_slider,
                    min=0,
                    max=1,
                    marks={i / 10: str(i / 10) for i in range(11)},
                    step=0.01,
                    value=0.5,
                    dots=True
                ), style={"margin": '-1% 20% 0% 3%'})], width=7,
            id="consensus_tree_col"),
        dbc.Col(children=[
            html.H5("Metadata in affinity tree leaves:"),
            dcc.Dropdown(
                id=id_leaf_info_dropdown,
                style={'margin-bottom': '20px'},
                options=[],
                value='SEQID'
            ),
            html.H5([
                "Affinity tree node details:",
                html.P(id=id_consensus_node_details_header)
            ]),
            html.Img(
                id=id_consensus_node_details_distribution,
                style={'max-width': '100%',
                       'margin-bottom': '2%'}
            ),
            dcc.Loading(dash_table.DataTable(
                id=id_consensus_node_details_table,
                style_table={
                    'maxHeight': '800',
                    'overflowY': 'scroll'
                },
                style_cell={'textAlign': 'left'},
                sorting=True
            ), type="circle")], width=3)],
    className="vis_row")

_consensus_table_row = dbc.Row(
    children=[
        dbc.Col(html.H4("Consensuses on current cut level"), width=12),
        dbc.Col(
            html.Div(
                id=id_consensus_table_container,
                children=dcc.Loading(
                    dash_table.DataTable(
                        id=id_consensuses_table,
                        sorting=True,
                        sorting_type="multi"),
                    type="circle")), width=12,
            style={'overflow-x': 'scroll'})], className="vis_row")

loading_style = "circle"
_pangviz_tab_content = dbc.Container([
    dcc.Store(id=id_visualisation_session_info, data=""),
    dcc.Store(id=id_elements_cache_info, data=""),
    dbc.Row(
        style={'display': 'none'},
        children=[
            html.Div(id=id_pangenome_hidden),
            html.Div(id=id_poagraph_hidden),
            html.Div(id=id_full_consensustree_hidden),
            html.Div(id=id_partial_consensustable_hidden),
            html.Div(id=id_current_consensustree_hidden),
            html.Div(id=id_full_consensustable_hidden),
            html.Div(id=id_consensus_node_details_table_hidden)]),
    _load_pangenome_row,
    dbc.Collapse(
        id=id_pangviz_result_collapse,
        children=[
            _task_parameters_row,
            _input_data_row,
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
                    html.P(f"Poagraph nodes count: {len(jsonpangenome.nodes)}"),
                    html.P(f"Sequences count: {len(jsonpangenome.sequences)}"),
                    html.P(
                        f"Consensuses count: {len(jsonpangenome.consensuses)}"),
                ], className='card-text'),
            ]),
            dbc.CardFooter("Processing info", className="text-center")
        ], outline=True, color="dark"),
    ])
