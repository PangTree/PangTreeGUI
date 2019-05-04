from io import StringIO
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..components import tools, processing
from ..layout.layout_ids import *
from ..server import app


@app.callback(Output(id_metadata_upload_state, 'data'),
              [Input('metadata_upload', 'contents')],
              [State('metadata_upload', 'filename'),
               State(id_session_state, 'data')])
def validate_metadata_file(file_content, file_name, session_state):
    if file_content is None or file_name is None:
        return None
    else:
        file_content = StringIO(tools.decode_content(file_content))
        error_message = processing.metadata_file_is_valid(file_content)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}


@app.callback(Output(id_metadata_upload_state_info, 'children'),
              [Input(id_metadata_upload_state, 'data')])
def show_metadata_validation_result(metadata_upload_state_data):
    if metadata_upload_state_data is None or len(metadata_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        if metadata_upload_state_data["is_correct"]:
            filename = metadata_upload_state_data["filename"]
            return [html.I(className="fas fa-check-circle correct"),
                    html.P(f"File {filename} uploaded.", style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(metadata_upload_state_data["error"], style={"display": "inline", "margin-left": "10px"})]


@app.callback(Output(id_metadata_upload_state_info, 'style'),
              [Input(id_metadata_upload_state, 'data')],
              [State(id_metadata_upload_state_info, 'style')])
def unhide_metadata_upload_info(metadata_upload_state_data, current_style):
    if metadata_upload_state_data is None or len(metadata_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        if not current_style:
            return {"visibility": "visible"}
        current_style["visibility"] = "visible"
        return current_style


# EXAMPLE DATASETS

@app.callback(
    Output("balibase_collapse", "is_open"),
    [Input("collapse-balibase-button", "n_clicks")],
    [State("balibase_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("ebola_collapse", "is_open"),
    [Input("collapse-ebola-button", "n_clicks")],
    [State("ebola_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("fabricated_collapse", "is_open"),
    [Input("collapse_fabricated_button", "n_clicks")],
    [State("fabricated_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
