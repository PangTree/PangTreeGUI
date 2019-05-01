import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_cytoscape as cyto
from dash_app.layout.layout_ids import *
from .css_styles import colors3 as colors
from ..components import poagraph as poagraph_component
from ..components import mafgraph as mafgraph_component


def get_tools_tab_content(get_url_function):
    return html.Div(className="tab-content",
                    children=[
                        html.Div(id="tools_intro",
                                 children=[]),
                        dcc.Tabs(id="tabs-tools", value='process', children=[
                            dcc.Tab(label='Multialignment processing',
                                    value='process',
                                    className='tools-tab',
                                    selected_className='tools-tab--selected',
                                    children=get_process_tab_content(get_url_function)),
                            dcc.Tab(label='Visualisation',
                                    value='vis',
                                    className='tools-tab',
                                    selected_className='tools-tab--selected',
                                    children=get_vis_tab_content())
                        ], className='tools-tabs',
                                 ),

                    ])


def get_process_tab_content(get_url_function):
    return [html.Div(
        id=id_process_tab_content,
        children=[
            dcc.Store(id=id_session_state),
            html.Div(className="params_section",
                     children=[html.H4("PoaGraph Construction"),
                               html.Div(className="param",
                                        children=[html.Div("Data type", className="two columns param_name"),
                                                  dcc.RadioItems(
                                                      options=[
                                                          {'label': 'Nucleotides', 'value': 'N'},
                                                          {'label': 'Proteins', 'value': 'P'},
                                                      ],
                                                      value='N'
                                                      , className="seven columns"
                                                  ),
                                                  html.Div(
                                                      "Type of aligned sequences provided in the uploaded multialignment file.",
                                                      className="param_description three columns")]),

                               html.Div(className="param",
                                        id=id_metadata_upload_param,
                                        children=[
                                            html.Div("Metadata CSV",
                                                     className="two columns param_name"),
                                            html.Div(
                                                children=[
                                                    dcc.Store(id=id_metadata_upload_state),
                                                    html.Div(dcc.Upload(id="metadata_upload",
                                                                        multiple=False,
                                                                        children=[
                                                                            html.I(
                                                                                className='one column file_upload_img fas fa-file-csv fa-3x',
                                                                                style={
                                                                                    'line-height': 'inherit',
                                                                                    'padding-left': '5px',
                                                                                }
                                                                            ),
                                                                            html.Div(html.A(
                                                                                'Drag & drop CSV metadata file or choose file...'),
                                                                                className="ten columns")
                                                                        ]),
                                                             className="file_upload"),
                                                    html.Div(
                                                        id=id_metadata_upload_state_info,
                                                        style={'visibility': 'hidden',
                                                               'width': 'auto',
                                                               'margin-top': '5px'}
                                                    )
                                                ],
                                                className="seven columns"
                                            ),
                                            html.Div(
                                                [
                                                    "Provide csv with metadata about the sequences that enhance the visualisation. 'seqid' column is obligatory and must match sequences ids present in MULTIALIGNMENT file. Other columns are optional. Example file: ",
                                                    html.A(
                                                        href="https://github.com/meoke/pang/blob/master/data/Fabricated/f.maf",
                                                        target="_blank", children="example1.maf")],
                                                className="param_description three columns")]),

                               html.Div(className="param",
                                        children=[html.Div("Multialignment file",
                                                           className="two columns param_name"),

                                                  html.Div(
                                                      children=[
                                                          dcc.Store(
                                                              id=id_multalignment_upload_state),
                                                          html.Div(
                                                              dcc.Upload(id="multialignment_upload",
                                                                         multiple=False,
                                                                         children=[
                                                                             html.I(
                                                                                 className='one column file_upload_img fas fa-align-justify fa-3x',
                                                                                 style={
                                                                                     'line-height': 'inherit',
                                                                                     'padding-left': '5px',
                                                                                 }
                                                                             ),
                                                                             html.Div(html.A(
                                                                                 'Drag & drop MAF file or choose file...'),
                                                                                 className="ten columns")
                                                                         ]),
                                                              className="file_upload"),
                                                          html.Div(
                                                              id=id_multalignment_upload_state_info,
                                                              style={'visibility': 'hidden',
                                                                     'width': 'auto',
                                                                     'margin-top': '5px'}
                                                          )
                                                      ],
                                                      className="seven columns"
                                                  ),
                                                  html.Div(
                                                      children=[
                                                          "Multialignment file. Accepted formats: ",
                                                          html.A(
                                                              href="http://www1.bioinf.uni-leipzig.de/UCSC/FAQ/FAQformat.html#format5",
                                                              target="_blank", children="maf"), ", ",
                                                          html.A(
                                                              href="https://github.com/meoke/pang/blob/master/README.md#po-file-format-specification",
                                                              target="_blank", children="po"),
                                                          ". See example file: ",
                                                          html.A(
                                                              href="https://github.com/meoke/pang/blob/master/data/Fabricated/f.maf",
                                                              target="_blank",
                                                              children="example1.maf")],
                                                      className="param_description three columns")]),
                               html.Div(className="param_group",
                                        id=id_maf_specific_params,
                                        style={"display": "none", "overflow": "auto"},
                                        children=[
                                            html.Div(className="param",
                                                     children=[
                                                         html.Div("Missing nucleotides source",
                                                                  className="two columns param_name"),
                                                         dcc.RadioItems(
                                                             id=id_fasta_provider_choice,
                                                             options=[
                                                                 {'label': "NCBI", 'value': 'NCBI'},
                                                                 {'label': 'Fasta File',
                                                                  'value': 'File'},
                                                                 {'label': 'Custom symbol',
                                                                  'value': 'Symbol'},
                                                             ],
                                                             value='NCBI'
                                                             , className="seven columns"
                                                         ),
                                                         html.Div(
                                                             "MAF file may not inlcude full sequences. Specify source of missing nucleotides/proteins.",
                                                             className="param_description three columns")]),
                                            html.Div(className="param",
                                                     id=id_fasta_upload_param,
                                                     style={"display": "none"},
                                                     children=[
                                                         html.Div("Missing symbols file source",
                                                                  className="two columns param_name"),
                                                         html.Div(
                                                             children=[
                                                                 dcc.Store(id=id_fasta_upload_state),
                                                                 html.Div(
                                                                     dcc.Upload(id="fasta_upload",
                                                                                multiple=False,
                                                                                children=[
                                                                                    html.I(
                                                                                        className='one column file_upload_img fas fa-align-left fa-3x',
                                                                                        style={
                                                                                            'line-height': 'inherit',
                                                                                            'padding-left': '5px',
                                                                                        }
                                                                                    ),
                                                                                    html.Div(html.A(
                                                                                        'Drag & drop FASTA/ZIP file or choose file...'),
                                                                                        className="ten columns")
                                                                                ]),
                                                                     className="file_upload"),
                                                                 html.Div(
                                                                     id=id_fasta_upload_state_info,
                                                                     style={'visibility': 'hidden',
                                                                            'width': 'auto',
                                                                            'margin-top': '5px'}
                                                                 )
                                                             ],
                                                             className="seven columns"
                                                         ),
                                                         html.Div(
                                                             "Provide zip with fasta files or single fasta file. It must contain full sequeneces which are not fully represented in provided MAF file.",
                                                             className="param_description three columns")]),
                                            html.Div(className="param",
                                                     id=id_missing_symbol_param,
                                                     style={"display": "none"},
                                                     children=[
                                                         html.Div(
                                                             "Missing symbol for unknown nucleotides/proteins",
                                                             className="two columns param_name"),
                                                         html.Div(children=[

                                                             dcc.Input(id=id_missing_symbol_input,
                                                                       maxLength=1,
                                                                       minLength=1,
                                                                       type="text",
                                                                       value='?')
                                                         ],

                                                             className="seven columns"
                                                         ),
                                                         html.Div(
                                                             "Any single character is accepted but it must be present in BLOSUM file. Default BLOSUM file uses '?'.",
                                                             className="param_description three columns")])
                                        ])]),
            html.Div(className="params_section",
                     style={"overflow": "auto"},
                     children=[html.H4("Consensus Tree Generation"),
                               html.Div(className="param",
                                        children=[html.Div("BLOSUM file",
                                                           className="two columns param_name"),

                                                  html.Div(
                                                      children=[
                                                          dcc.Store(
                                                              id=id_blosum_upload_state),
                                                          html.Div(
                                                              dcc.Upload(id="blosum_upload",
                                                                         multiple=False,
                                                                         children=[
                                                                             html.I(
                                                                                 className='one column file_upload_img fas fa-table fa-3x',
                                                                                 style={
                                                                                     'line-height': 'inherit',
                                                                                     'padding-left': '5px',
                                                                                 }
                                                                             ),
                                                                             html.Div(html.A(
                                                                                 'Drag & drop BLOSUM file or choose file...'),
                                                                                 className="ten columns")
                                                                         ]),
                                                              className="file_upload"),
                                                          html.Div(
                                                              id=id_blosum_upload_state_info,
                                                              style={'visibility': 'hidden',
                                                                     'width': 'auto',
                                                                     'margin-top': '5px'}
                                                          )
                                                      ],
                                                      className="seven columns"
                                                  ),
                                                  html.Div(
                                                      children=[
                                                          "BLOSUM file. This parameter is optional as default BLOSUM file is ", html.A(
                                                              href="https://github.com/meoke/pang/blob/master/bin/blosum80.mat",
                                                              target="_blank", children="BLOSUM80"), ". The BLOSUM file must contain '?' or custom symbol for missing nucleotides/proteins if specified."],
                                                      className="param_description three columns")]),
                               html.Div(className="param",
                                        children=[
                                            html.Div("Algorithm",
                                                     className="two columns param_name"),
                                            dcc.RadioItems(
                                                id=id_tree_algorithm_choice,
                                                options=[
                                                    {'label': "Poa", 'value': 'poa'},
                                                    {'label': 'Tree', 'value': 'tree'},
                                                ],
                                                value='tree'
                                                , className="seven columns"
                                            ),
                                            html.Div(
                                                children=[
                                                    "There are two available algorithms for consensus tree generation. 'Poa' by ",
                                                    html.A(
                                                        "Lee et al.",
                                                        href="https://doi.org/10.1093/bioinformatics/18.3.452"),
                                                    " and 'Tree' algorithm described ",
                                                    html.A("here",
                                                           href="https://github.com/meoke/pang#idea-and-algorithm-description")],
                                                className="param_description three columns")]),
                               html.Div(className="param",
                                        id=id_hbmin_param,
                                        style={"display": "none"},
                                        children=[
                                            html.Div("HBMIN",
                                                     className="two columns param_name"),
                                            html.Div(children=[
                                                dcc.Input(id=id_hbmin,
                                                          max=1,
                                                          min=0,
                                                          type="number",
                                                          value=0.8)
                                            ],
                                                className="seven columns")
                                            ,
                                            html.Div(
                                                "HBMIN is required minimum value of similarity between sequence and assigned consensus.",
                                                className="param_description three columns")]),
                               html.Div(className="param_group",
                                        id=id_tree_specific_params,
                                        style={"display": "none"},
                                        children=[
                                            html.Div(className="param",
                                                     id=id_p_param,
                                                     children=[
                                                         html.Div("P",
                                                                  className="two columns param_name"),
                                                         html.Div(children=[
                                                             dcc.Input(id=id_p,
                                                                       min=0,
                                                                       type="number",
                                                                       value=1)
                                                         ],
                                                             className="seven columns")
                                                         ,
                                                         html.Div(
                                                             "P is used during cutoff search. P < 1 decreases distances between small compatibilities and increases distances between the bigger ones while p > 1 works in the opposite way.",
                                                             className="param_description three columns")]),
                                            html.Div(className="param",
                                                     id=id_stop_param,
                                                     children=[
                                                         html.Div("Stop",
                                                                  className="two columns param_name"),
                                                         html.Div(children=[
                                                             dcc.Input(id=id_stop,
                                                                       min=0,
                                                                       max=1,
                                                                       type="number",
                                                                       value=1)
                                                         ],
                                                             className="seven columns")
                                                         ,
                                                         html.Div(
                                                             "Minimum value of compatibility in tree leaves.",
                                                             className="param_description three columns")])

                                        ])
                               ]),
            html.Div(className="params_section",
                     children=[html.H4("Output Configuration"),
                               html.Div(
                                   className="param",
                                   children=[dcc.Checklist(
                                       id=id_output_configuration,
                                       options=[
                                           {
                                               'label': 'FASTA (all sequences and consensuses in fasta format)',
                                               'value': 'fasta'},
                                           {'label': 'PO (poagraph in PO format)', 'value': 'po'},
                                       ],
                                       values=['fasta', 'po'],
                                       className="nine columns"
                                   ),
                                       html.Div(
                                           children=[html.P("Output of the program will contain:"),
                                                     html.Ul(children=[
                                                         html.Li(
                                                             "JSON that can be used as Visualisation input."),
                                                         html.Li("LOG file"),
                                                         html.Li(
                                                             "Intermediate PO files produced by consensus algorithm.")]),
                                                     html.P(
                                                         "but also additional output can be produced.")],
                                           className="param_description three columns"
                                       )]
                               ),
                               html.Div(
                                   className="param",
                                   children=[dcc.Checklist(
                                       id=id_jump_to_vis,
                                       options=[
                                           {'label': 'Jump to visualisation after processing',
                                            'value': 'jump'},
                                       ],
                                       values=['jump'],
                                       className="nine columns"
                                   ),
                                       html.Div(
                                           "Immediately after processing jump to Visualisation tab and load the processing result.",
                                           className="param_description three columns"
                                       )]
                               )

                               ]),

            html.Button(id=id_pang_button,
                        children="Process",
                        className='button-primary form_item',
                        n_clicks_timestamp=0),
        ]
    )]


def get_vis_tab_content():
    return html.Div(
        id="vis_tab_content",
        children=[html.Div(id="tools_load_section",
                           children=[
                               html.Div(dcc.Upload(id=id_pangenome_upload,
                                                   children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                                                   multiple=False, ),
                                        className='three columns'),
                               html.Div(children="or load example data: ",
                                        style={'display': 'None', 'textAlign': 'center', 'lineHeight': '60px'},
                                        className='two columns'),
                               dcc.Dropdown(id="example_data_dropdown",
                                            options=[{'label': 'Ebola', 'value': 'Ebola'}],
                                            value='Ebola',
                                            className='five columns form_item'),
                               html.Button(id=id_load_pangenome_button,
                                           children=["Load pangenome"],
                                           className='button-primary form_item')
                           ]
                           ),
                  html.Div(id="tools_info_section",
                           children=[
                               html.Div(id=id_program_parameters,
                                        className='three columns section'),
                               html.Div(id=id_pangenome_info,
                                        className='nine columns section')]
                           ),
                  html.Div(id=id_mafgraph,
                           children=[
                               html.Div(id=id_mafgraph_container,
                                        className='twelve columns section row',
                                        children=[cyto.Cytoscape(id=id_mafgraph_graph,
                                                                 elements=[],
                                                                 layout={'name': 'cose'},
                                                                 style={'width': 'auto', 'height': '300px'},
                                                                 stylesheet=mafgraph_component.get_mafgraph_stylesheet(),
                                                                 # autolock=True,
                                                                 boxSelectionEnabled=False,
                                                                 autoungrabify=True,
                                                                 autounselectify=True)])
                           ]),
                  html.Div(id="tools_poagraph_section",
                           children=[html.Div(id=id_poagraph_container,
                                              className='twelve columns section row',
                                              children=[html.Div(id=id_poagraph_node_info),
                                                        cyto.Cytoscape(id=id_poagraph,
                                                                       layout={
                                                                           'name': 'preset'},
                                                                       stylesheet=poagraph_component.get_poagraph_stylesheet(),
                                                                       elements=[
                                                                       ],
                                                                       style={'width': 'auto', 'height': '500px'},
                                                                       # zoom=1,
                                                                       # minZoom=0.9,
                                                                       # maxZoom=1.1,
                                                                       # panningEnabled=False,
                                                                       # userPanningEnabled=False,
                                                                       boxSelectionEnabled=False,
                                                                       autoungrabify=True,
                                                                       autolock=True,
                                                                       autounselectify=True
                                                                       )

                                                        ]),
                                     html.Div(id=id_full_pangenome_container,
                                              className="twelve columns section row",
                                              children=[dcc.Graph(
                                                  id=id_full_pangenome_graph,
                                                  style={'width': 'auto'},
                                                  # style={'height': '400px', 'width': 'auto'},
                                                  figure={},
                                                  config={
                                                      'displayModeBar': False,
                                                  }
                                              )])
                                     ]
                           ),
                  html.Div(id=id_consensus_tree_container,
                           style={'display': 'none'},
                           children=[
                               html.Div(
                                   id='tree',
                                   children=[
                                       html.Div(
                                           id='graphics',
                                           children=[
                                               dcc.Graph(
                                                   id=id_consensus_tree_graph,
                                                   style={'height': '1000px', 'width': 'auto'}
                                               ),
                                               html.Div(
                                                   [html.Div(
                                                       dcc.Slider(
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
                                                       ),
                                                       style={'margin-top': '1%'},
                                                       className='ten columns'
                                                   ),
                                                       html.P(
                                                           id='consensus_tree_slider_value',
                                                           style={'font-size': 'large'},
                                                           className='two columns'
                                                       )],
                                                   className='row',
                                                   style={'margin-left': '3%',
                                                          'margin-right': '2%',
                                                          'margin-top': '-7%'}
                                               ),
                                           ],
                                           className='nine columns'
                                       ),
                                       html.Div(
                                           id='tree_info',
                                           children=[
                                               html.H5("Metadata in consensuses tree leaves:"),
                                               dcc.Dropdown(
                                                   id=id_leaf_info_dropdown,
                                                   style={'margin-bottom': '20px'},
                                                   options=[
                                                   ],
                                                   value='SEQID'
                                               ),
                                               html.H5("Consensus tree node details:"),
                                               html.H5(
                                                   id=id_consensus_node_details_header
                                               ),
                                               html.Img(
                                                   id=id_consensus_node_details_distribution,
                                               ),
                                               dash_table.DataTable(
                                                   id=id_consensus_node_details_table,
                                                   style_table={
                                                       'maxHeight': '800',
                                                       'overflowY': 'scroll'
                                                   },
                                                   style_cell={'textAlign': 'left'},
                                                   sorting=True
                                               )
                                           ],
                                           style={'padding-top': '7%', 'padding-right': '2%'},
                                           className='three columns'
                                       )
                                   ],
                                   className='row'
                               ),
                               html.Div(
                                   children=[html.Div(
                                       id='consensus_table_info',
                                       children=[
                                           dcc.Markdown("t",  # texts.table_info_markdown,
                                                        className='ten columns'),
                                           html.A(html.Button("Download table as csv",
                                                              id="csv_download",
                                                              disabled=False,
                                                              className='form_item two columns'),
                                                  href='download_csv'),
                                           html.Div(id='hidden_csv_generated',
                                                    style={'display': 'none'})
                                       ],
                                       style={'padding': '2%'}
                                   ),
                                   ],
                                   style={'margin-top': '25px'},
                               )
                           ]
                           ),
                  html.Div(id="consensus_table_container",
                           children=[dash_table.DataTable(id=id_consensuses_table,
                                                          sorting=True,
                                                          sorting_type="multi"),
                                     ],
                           style={'display': 'none'}, className='row')
                  ]
    )
