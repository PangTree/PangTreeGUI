import dash_bootstrap_components as dbc
import dash_html_components as html


def get_layout():
    return dbc.Container(
        html.Div([
            dbc.Jumbotron(children=[dbc.Row(
                [dbc.Col([html.H1("PoaPangenome"),
                          html.P("is a tool for analysis and visualisation of multiple sequence alignment.")],
                         className="col-md-8"),
                 dbc.Col(html.I(className="fas fa-seedling fa-10x"), className="col-md-4")])]),
            dbc.Row(html.H2("Key Features")),
            dbc.Row(dbc.CardDeck(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(dbc.Row([dbc.Col(html.I(className="fas fa-seedling fa-3x"), className="col-md-3"),
                                                     html.P("Build", className="col-md-9")])),
                            dbc.CardBody(
                                [
                                    dbc.CardText(
                                        "Multialignment is processed as Partial Order Alignment graph - poagraph"),
                                ]
                            ),
                        ]
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.CardTitle("This card has a title"),
                                    dbc.CardText("and some text, but no header"),
                                ]
                            )
                        ],
                        outline=True,
                        color="primary",
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.CardTitle("This card has a title"),
                                    dbc.CardText("and some text, and a footer!"),
                                ]
                            ),
                            dbc.CardFooter("Footer"),
                        ],
                        outline=True,
                        color="dark",
                    ),
                ]
            )
            )])
    )
