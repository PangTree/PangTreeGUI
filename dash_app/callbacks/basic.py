from dash.dependencies import Input, Output

from dash_app.app import app
from dash_app.components import pages


@app.callback(
    [
        Output("page_content", 'children'),
        Output("index_nav", 'className'),
        Output("pangbuild_nav", 'className'),
        Output("pangtreevis_nav", 'className'),
        Output("faq_nav", 'className')
    ],
    [
        Input("url", 'pathname')
    ]
)
def display_page(pathname):
    if pathname == '/faq':
        return pages.faq(), "", "", "", "active_link"
    elif pathname == '/pangtreebuild':
        return pages.pangtreebuild(), "", "active_link", "", ""
    elif pathname == '/pangtreevis':
        return pages.pangtreevis(), "", "", "active_link", ""
    else:
        return pages.index(), "active_link", "", "", ""
