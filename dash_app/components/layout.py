import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def get_nav_link(fa_icon: str, span_text: str, href: str, id: str) -> html.Li:
    return html.Li(
        html.A(
            [
                html.I(className=f"fas fas-nav {fa_icon}"), 
                html.Span(span_text, className="nav-text")
            ],
            href=href, 
            id=id
        ), 
        className="has-subnav high"
    )


def generate_layout() -> html.Div:
    navbar_list = html.Ul(
        [
            get_nav_link("fa-home", "Home", "/#", "index_nav"),
            get_nav_link("fa-seedling", "PangTreeBuild", "/pangtreebuild", "pangbuild_nav"),
            get_nav_link("fa-tree", "PangTreeVis", "/pangtreevis", "pangtreevis_nav"),
            get_nav_link("fa-question-circle", "FAQ", "/faq", "faq_nav"),
        ]
    )
    return html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div([], className="area"),
        dbc.Navbar(
            className="main-menu", 
            children=navbar_list,
            sticky="left",
        ),
        html.Div(id="page_content", style={'margin-left': '60px'})
    ]
)



