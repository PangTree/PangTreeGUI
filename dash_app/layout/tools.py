import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_cytoscape as cyto
from dash_app.layout.layout_ids import *


def get_tools_tab_content():
    return html.Div(className="tab-content",
                    children=[
                        html.Div(id="tools_intro",
                                 children=[]),
                        dcc.Tabs(id="tabs-tools", value='vis', children=[
                            dcc.Tab(label='Multialignment processing',
                                    value='process',
                                    className='tools-tab',
                                    selected_className='tools-tab--selected',
                                    children=get_process_tab_content()),
                            dcc.Tab(label='Visualisation',
                                    value='vis',
                                    className='tools-tab',
                                    selected_className='tools-tab--selected',
                                    children=get_vis_tab_content())
                        ], className='tools-tabs',
                                 )
                    ])


def get_process_tab_content():
    return html.Div(
        html.Button(id=id_pang_button,
                    children="Process",
                    className='button-primary form_item')
    )


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
                  html.Div(id="tools_poagraph_section",
                           style={'display': 'none'},
                           children=[html.Div(id=id_poagraph_container,
                                              className='twelve columns section row',
                                              children=[cyto.Cytoscape(id=id_poagraph,
                                                                       layout={'name': 'preset'},
                                                                       stylesheet=[
                                                                           {
                                                                               'selector': 'node',
                                                                               'style': {
                                                                                   'background-color': 'white',
                                                                               }
                                                                           },
                                                                           {
                                                                               'selector': '.s_node',
                                                                               'style': {
                                                                                   'border-color': 'green',
                                                                                   'border-width': '0.5px',
                                                                                   'content': 'data(label)',
                                                                                   'height': '10px',
                                                                                   'width': '10px',
                                                                                   'text-halign': 'center',
                                                                                   'text-valign': 'center',
                                                                                   'font-size': '5px',
                                                                                   'shape': 'roundrectangle',
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
                                                                                   'haystack-radius': 0.7,
                                                                                   'width': '2px',
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
                                                                                   'width': '1px'
                                                                               }
                                                                           },
                                                                       ],
                                                                       elements=[
                                                                       ],
                                                                       style={'width': 'auto', 'height': '500px'}, )
                                                        ]),
                                     html.Div(id=id_full_pangenome_container,
                                              className="twelve columns section row",
                                              # style={'background-color': 'red'},
                                              children=[dcc.Graph(
                                                  id=id_full_pangenome_graph,
                                                  style={'height': '400px', 'width': 'auto'},
                                                  figure=[],
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
