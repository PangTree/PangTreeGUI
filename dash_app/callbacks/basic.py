import dash
from dash.dependencies import Input, Output

from dash_app.app import app
from dash_app.components import pages


@app.callback(
    [
        Output("page_content_index", 'style'),
        Output("page_content_faq", 'style'),
        Output("page_content_pangtreebuild", 'style'),
        Output("page_content_pangtreevis", 'style'),
        Output("index_nav", 'className'),
        Output("pangbuild_nav", 'className'),
        Output("pangtreevis_nav", 'className'),
        Output("faq_nav", 'className')
    ],
    [
        Input("index_nav", 'n_clicks'),
        Input("pangbuild_nav", 'n_clicks'),
        Input("pangtreevis_nav", 'n_clicks'),
        Input("faq_nav", 'n_clicks'),
        Input("logo_pangtreebuild", 'n_clicks'),
        Input("logo_pangtreevis", 'n_clicks'),
    ]
)
def display_page(
        index_nav,
        pangtreebuild_nav,
        pangtreevis_nav,
        faq_nav,
        build_logo,
        vis_logo,
    ):
    ctx = dash.callback_context

    if not ctx.triggered:
        trigger = "index_nav"
    else:
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    display_true = {"diaplay": "flex"}
    display_false = {"display": "none"}
    if trigger == 'faq_nav':
        return (
            display_false,
            display_true,
            display_false,
            display_false,
            "", 
            "", 
            "", 
            "active_link",
        )
    elif trigger == 'pangbuild_nav' or trigger == "logo_pangtreebuild":
        return (
            display_false,
            display_false,
            display_true,
            display_false,
            "", 
            "active_link", 
            "", 
            "",
        )
    elif trigger == 'pangtreevis_nav' or trigger == "logo_pangtreevis":
        return (
            display_false,
            display_false,
            display_false,
            display_true,
            "", 
            "", 
            "active_link", 
            "",
        )
    else:
        return (
            display_true,
            display_false,
            display_false,
            display_false,
            "active_link", 
            "", 
            "", 
            "",
        )
