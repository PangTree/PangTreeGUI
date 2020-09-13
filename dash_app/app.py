import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dash_app.layout import pages
from dash_app.server import app

from .callbacks import consensustable
from .callbacks import consensustree
from .callbacks import poagraph
from .callbacks import pangtreebuild
from .callbacks import visualisation

app.title = 'PangtreeVis'
app.css.config.serve_locally = False
app.scripts.config.serve_locally = True

external_css = [
    'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    # dbc.themes.FLATLY
]
for css in external_css:
    app.css.append_css({"external_url": css})

def get_nav_link(fa_icon, span, href, id):
    return html.Li(html.A(
        [
            html.I(className=f"fas fas-nav {fa_icon}"), 
            html.Span(span, className="nav-text")
        ],
        href=href, 
        id=id), className="has-subnav high")


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div([], className="area"),
    dbc.Navbar([
        html.Ul([
            get_nav_link("fa-home", "Home", "/#", "index_nav"),
            get_nav_link("fa-seedling", "PangTreeBuild", "/pangtreebuild", "pangbuild_nav"),
            get_nav_link("fa-tree", "PangTreeVis", "/pangtreevis", "pangtreevis_nav"),
            get_nav_link("fa-question-circle", "FAQ", "/faq", "faq_nav"),
        ])
    ], className="main-menu", sticky="left"),
    html.Div(id="page_content", style={'margin-left': '60px'})
])


@app.callback([Output("page_content", 'children'),
               Output("index_nav", 'className'),
               Output("pangbuild_nav", 'className'),
               Output("pangtreevis_nav", 'className'),
               Output("faq_nav", 'className')],
              [Input("url", 'pathname')])
def display_page(pathname):
    if pathname == '/faq':
        return pages.faq(), "", "", "", "active_link"
    elif pathname == '/pangtreebuild':
        return pages.pangtreebuild(), "", "active_link", "", ""
    elif pathname == '/pangtreevis':
        return pages.pangtreevis(), "", "", "active_link", ""
    else:
        return pages.index(), "active_link", "", "", ""

