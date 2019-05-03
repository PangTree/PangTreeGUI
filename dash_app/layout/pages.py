import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc


def contact():
    return dbc.Container(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.CardTitle("Norbert Dojer, PhD.", className="text-info"),
                            dbc.CardText(html.P("dojer@mimuw.edu.pl")),
                        ]
                    ),
                ],
                outline=True,
                color="info"
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.CardTitle("Paulina Dziadkiewicz, B.Sc.", className="text-info"),
                            dbc.CardText("pedziadkiewicz@gmail.com"),
                        ]
                    )
                ],
                outline=True,
                color="info",
            )
        ]
    )


def index():
    return dbc.Container(
        html.Div([
            dbc.Jumbotron(children=[dbc.Row(
                [dbc.Col([html.H2("PoaPangenome"),
                          html.P("is a tool for multiple sequence alignment analysis."),
                          html.H2("PangViz"),
                          html.P("visualises the results in browser.")
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
                                                        href="https://github.com/meoke/pang/blob/master/README.md#po-file-format-specification",
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
                                                      html.Li([html.Strong("Consensus Tree"),
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
                                                html.Ul([html.Li(
                                                    "MAF blocks graph"),
                                                    html.Li("Multiple sequence alignment as Partial Order Graph"),
                                                    html.Li("Consensus tree"),
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
                                             html.A("GitHub", href="https://github.com/meoke/pang", target="_blank"),
                                             " and ",
                                             html.A("PyPI", href="", target="_blank"),
                                             ". It can be incorporated into your Python application in this simple way:"])),
                          dbc.Card(dbc.CardBody(dcc.Markdown('''

                          
                          from poapangenome import Poagraph, input_types, fasta_provider, consensus

                          poagraph = Poagraph.build_from_dagmaf(input_types.Maf("example.maf"), 
                                                                fasta_provider.FromNCBI())
                          consensus_tree = consensus.tree_generator.get_consensus_tree(poagraph,
                                                                                       Blosum("BLOSUM80.mat"),
                                                                                       output_dir,
                                                                                       stop=1,
                                                                                       p=1)
                          pangenomejson = to_PangenomeJSON(poagraph, consensus_tree)
                          
                          ''')), style={"margin": '30px 0px', 'padding': '10px'}),
                          dbc.Row("or used as a CLI tool:"),
                          dbc.Card(dbc.CardBody(dcc.Markdown(
                              '''poapangenome --multialignment "example.maf" --consensus tree --p 1 --stop 1''')),
                              style={"margin": '30px 0px', 'padding': '10px'}),
                          dbc.Row("Check out full documentation at the above links.")
                          ]
                         )


def tools():
    return html.Div([
        dbc.Jumbotron(children=[dbc.Row(
            [dbc.Col(dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.CardText(
                                html.Ul([html.Li(
                                    [html.Span(html.I(className="fas fa-file"), className="fa-li"), "multialignment ",
                                     html.A("MAF",
                                            href="http://www1.bioinf.uni-leipzig.de/UCSC/FAQ/FAQformat.html#format5",
                                            target="_blank"), " or ",
                                     html.A("PO",
                                            href="https://github.com/meoke/pang/blob/master/README.md#po-file-format-specification",
                                            target="_blank")]),
                                    html.Li([html.Span(html.I(className="fas fa-file"), className="fa-li"),
                                             "metadata CSV"]),
                                    html.Li([html.Span(html.I(className="fas fa-sliders-h"), className="fa-li"),
                                             "additional parameters"])], className="fa-ul")
                            )
                        ]
                    ),
                ], outline=True
            ), className="col-md-2"),
                dbc.Col(html.I(className="fas fa-arrow-right"), className="col-md-1 my-auto text-center"),
                dbc.Col(html.H2(dbc.Badge("PoaPangenome", className="badge-success badge-pill")),
                        className="col-md-2 my-auto"),
                dbc.Col(html.I(className="fas fa-arrow-right"), className="col-md-1 my-auto text-center"),
                dbc.Col(dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                dbc.CardText(dbc.Row(
                                    [
                                        dbc.Col(html.I(className="fas fa-file"), className="col-md-3"),
                                        dbc.Col("pangenome.json"),
                                    ],
                                    align="center",
                                    no_gutters=True,
                                ))
                            ]
                        ),
                    ]
                ), className="col-md-2 my-auto"),
                dbc.Col(html.I(className="fas fa-arrow-right"), className="col-md-1 my-auto text-center"),
                dbc.Col(html.H2(dbc.Badge("PangViz", className="badge-success badge-pill")),
                        className="col-md-2 my-auto"),
            ]
        )]),
        dbc.Tabs(
            [
                dbc.Tab(_poapangenome_tab_content, label="PoaPangenome", tab_style={"margin-left": "auto"}),
                dbc.Tab(_pangviz_tab_content, label="PangViz", label_style={"color": "#00AEF9"}),
            ], className="nav-justified"
        )
    ])


_poapangenome_tab_content = html.Div("a")
_pangviz_tab_content = html.Div("b")
