from dash.dependencies import Input, Output
import dash_html_components as html
from dash_app.components import tools
from dash_app.layout.layout_ids import *

from dash_app.server import app

@app.callback(
    Output(id_program_parameters, 'children'),
    [Input(id_pangenome_parameters_hidden, 'children')]
)
def update_pangenome_parameters(jsonified_params):
    if not jsonified_params:
        return []
    parameters = tools.unjsonify_builtin_types(jsonified_params)
    params_info = []
    for param_name, param_value in parameters.items():
        params_info.append(html.P(f"{param_name}: {param_value}"))
    return params_info
