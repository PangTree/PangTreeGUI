import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
from .server import app
from .layout import layout_ids, pages

app.title = 'PoaPangenome'

external_css = [
    'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    dbc.themes.FLATLY
]
for css in external_css:
    app.css.append_css({"external_url": css})

app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    [dcc.Location(id=layout_ids.id_url, refresh=False),
     dbc.Navbar(
         [
             html.A(
                 dbc.Row(
                     [
                         dbc.Col(html.Img(src="assets/favicon.ico", height="30px")),
                         dbc.Col(dbc.NavbarBrand("Pangenome Tools", className="ml-2")),
                     ],
                     align="center",
                     no_gutters=True,
                 ),

                 href="/#",
             ),
             dbc.NavbarToggler(id="navbar-toggler"),
             dbc.Collapse(dbc.Row(children=[
                 dbc.Col(dbc.NavLink("Tools", href="/tools")),
                 dbc.Col(dbc.NavLink("Package", href="/package")),
                 dbc.Col(dbc.NavLink("Contact", href="/contact")),
             ],
                 no_gutters=True,
                 className="ml-auto flex-nowrap mt-3 mt-md-0",
                 align="center"), id="navbar-collapse", navbar=True)
         ],
         sticky="top",
     ),
     html.Div(id=layout_ids.id_page_content)])
# children=layout.get_page_content(app.get_asset_url))])

tools = html.Div("tools")
package = html.Div("package")
contact = html.Div("contact")


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(Output(layout_ids.id_page_content, 'children'),
              [Input(layout_ids.id_url, 'pathname')])
def display_page(pathname):
    if pathname == '/tools':
        return pages.tools()
    elif pathname == '/package':
        return pages.package()
    elif pathname == '/contact':
        return pages.contact()
    else:
        return pages.index()

# from .callbacks import visualisation
# from .callbacks import broadcast_pangenome
# # from .callbacks import parameters
# from .callbacks import consensustable
# from .callbacks import consensustree
# from .callbacks import mafgraph
# from .callbacks import poagraph
# from .callbacks import processing

from .callbacks import poapangenome
from .callbacks import visualisation