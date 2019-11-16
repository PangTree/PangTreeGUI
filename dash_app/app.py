import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from .layout import layout_ids, pages
from .server import app

app.title = 'PangtreeVis'
# app.css.config.serve_locally = True
# app.scripts.config.serve_locally = True


external_css = [
    'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    # dbc.themes.FLATLY
]
for css in external_css:
    app.css.append_css({"external_url": css})

app.config.suppress_callback_exceptions = True
draw_poagraph = True

app.layout = html.Div([
    dcc.Location(id=layout_ids.id_url, refresh=False),
    html.Div([], className="area"),
    dbc.Navbar([
        html.Ul([
            html.Li(html.A([html.I(className="fas fas-nav fa-home"),
                            html.Span("Home", className="nav-text")],
                           href="/#"), className="high"),
            html.Li(html.A([html.I(className="fas fas-nav fa-seedling"),
                            html.Span("PangTreeBuild", className="nav-text")],
                           href="/pangtreebuild"), className="has-subnav high"),
            html.Li(html.A([html.I(className="fas fas-nav fa-tree"),
                            html.Span("PangTreeVis", className="nav-text")],
                           href="/pangtreevis"), className="has-subnav high"),
            html.Li(html.A([html.I(className="fas fas-nav fa-archive"),
                            html.Span("Package", className="nav-text")],
                           href="/package"), className="has-subnav high"),
            html.Li(html.A([html.I(className="fas fas-nav fa-address-book"),
                            html.Span("Contact", className="nav-text")],
                           href="/contact"), className="has-subnav high"),
        ])
    ], className="main-menu", sticky="left"),
    html.Div(id=layout_ids.id_page_content, style={'margin-left': '60px'})
])


@app.callback(Output(layout_ids.id_page_content, 'children'),
              [Input(layout_ids.id_url, 'pathname')])
def display_page(pathname):
    if pathname == '/contact':
        return pages.contact()
    elif pathname == '/package':
        return pages.package()
    elif pathname == '/pangtreebuild':
        return pages.pangtreebuild()
    elif pathname == '/pangtreevis':
        return pages.pangtreevis()
    else:
        return pages.index()


from .callbacks import consensustable
from .callbacks import consensustree
from .callbacks import mafgraph
from .callbacks import poagraph

from .callbacks import pangtreebuild
from .callbacks import visualisation
