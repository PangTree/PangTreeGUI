import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dash_app.components import layout
from dash_app.settings import APP_SETTINGS

app = dash.Dash(
    __name__,
    external_stylesheets=APP_SETTINGS["stylesheets"],
    suppress_callback_exceptions=True,
    title=APP_SETTINGS["title"],
    update_title=None
)

def get_nav_link(fa_icon, span, href, id):
    return html.Li(
        html.A(
            [
                html.I(className=f"fas fas-nav {fa_icon}"), 
                html.Span(span, className="nav-text")
            ],
            href=href, 
            id=id
        ), 
        className="has-subnav high"
    )


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div([], className="area"),
        dbc.Navbar(
            [
                html.Ul(
                    [
                        get_nav_link("fa-home", "Home", "/#", "index_nav"),
                        get_nav_link("fa-seedling", "PangTreeBuild", "/pangtreebuild", "pangbuild_nav"),
                        get_nav_link("fa-tree", "PangTreeVis", "/pangtreevis", "pangtreevis_nav"),
                        get_nav_link("fa-question-circle", "FAQ", "/faq", "faq_nav"),
                    ]
                )
            ], 
            className="main-menu", 
            sticky="left"
        ),
        html.Div(id="page_content", style={'margin-left': '60px'})
    ]
)


@app.callback([Output("page_content", 'children'),
               Output("index_nav", 'className'),
               Output("pangbuild_nav", 'className'),
               Output("pangtreevis_nav", 'className'),
               Output("faq_nav", 'className')],
              [Input("url", 'pathname')])
def display_page(pathname):
    if pathname == '/faq':
        return layout.faq(), "", "", "", "active_link"
    elif pathname == '/pangtreebuild':
        return layout.pangtreebuild(), "", "active_link", "", ""
    elif pathname == '/pangtreevis':
        return layout.pangtreevis(), "", "", "active_link", ""
    else:
        return layout.index(), "active_link", "", "", ""

