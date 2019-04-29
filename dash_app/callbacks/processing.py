from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
from ..server import app
from ..layout.layout_ids import *
from ..components import processing
from ..components import jsontools

@app.callback(Output(id_multalignment_upload_state, 'data'),
              [Input('multialignment_upload', 'contents')],
              [State('multialignment_upload', 'filename')])
def validate_multialignment(file_content, file_name):
    if file_content is None or file_name is None:
        return {}
    else:
        file_content = jsontools.decode_content(file_content)
        error_message = processing.multialignment_file_is_valid(file_content, file_name)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}


@app.callback(Output(id_multalignment_upload_state_img, 'className'),
              [Input(id_multalignment_upload_state, 'data')])
def validate_multialignment(multialignment_upload_state_data):
    if multialignment_upload_state_data is None or len(multialignment_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        if multialignment_upload_state_data["is_correct"]:
            return "correct_param"

@app.callback(Output(id_multalignment_upload_state_img, 'children'),
              [Input(id_multalignment_upload_state, 'data')])
def validate_multialignment(multialignment_upload_state_data):
    if multialignment_upload_state_data is None or len(multialignment_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        if multialignment_upload_state_data["is_correct"]:
            filename = multialignment_upload_state_data["filename"]
            return [html.I(className="fas fa-check-circle correct"), html.P(f"File {filename} uploaded.", style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(multialignment_upload_state_data["error"], style={"display": "inline", "margin-left": "10px"})]


@app.callback(Output(id_multalignment_upload_state_img, 'style'),
              [Input(id_multalignment_upload_state, 'data')],
              [State(id_multalignment_upload_state_img, 'style')])
def validate_multialignment(multialignment_upload_state_data, current_style):
    if multialignment_upload_state_data is None or len(multialignment_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        current_style["visibility"] = "visible"
        return current_style