from io import StringIO
from pathlib import Path

import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..components import tools, processing
from ..layout.layout_ids import *
from ..server import app


def get_success_info(message):
    return [html.I(className="fas fa-check-circle correct"),
            html.P(message, style={"display": "inline", "margin-left": "10px"})]


def get_error_info(message):
    return [html.I(className="fas fa-exclamation-circle incorrect"),
            html.P(message, style={"display": "inline", "margin-left": "10px"})]

# Metadata Validation

@app.callback(Output(id_metadata_upload_state, 'data'),
              [Input(id_metadata_upload, 'contents')],
              [State(id_metadata_upload, 'filename'),
               State(id_session_state, 'data')])
def validate_metadata_file(file_content, file_name, session_state):
    if file_content is None or file_name is None:
        return None
    else:
        file_content = tools.decode_content(file_content)
        error_message = processing.metadata_file_is_valid(file_content, file_name)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}


@app.callback(Output(id_metadata_upload_state_info, 'children'),
              [Input(id_metadata_upload_state, 'data')])
def show_validation_result(upload_state_data):
    if upload_state_data is None or len(upload_state_data) == 0:
        return []
    else:
        if upload_state_data["is_correct"]:
            filename = upload_state_data["filename"]
            return get_success_info(f"File {filename} uploaded.")
        else:
            return get_error_info(upload_state_data["error"])

# Multialignment validation

@app.callback(Output(id_multialignment_upload_state, 'data'),
              [Input(id_multialignment_upload, 'contents')],
              [State(id_multialignment_upload, 'filename')])
def validate_metadata_file(file_content, file_name):
    if file_content is None or file_name is None:
        return None
    else:
        file_content = tools.decode_content(file_content)
        error_message = processing.multialignment_file_is_valid(file_content, file_name)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}


@app.callback(Output(id_multialignment_upload_state_info, 'children'),
              [Input(id_multialignment_upload_state, 'data')])
def show_multialignment_validation_result(upload_state_data):
    if upload_state_data is None or len(upload_state_data) == 0:
        return []
    else:
        if upload_state_data["is_correct"]:
            filename = upload_state_data["filename"]
            return get_success_info(f"File {filename} uploaded.")
        else:
            return get_error_info(upload_state_data["error"])



# MAF specific parameters toggling

@app.callback(Output(id_maf_specific_params, 'is_open'),
              [Input(id_multialignment_upload_state, 'data')])
def toggle_maf_specific_params(multialignment_upload_state_data):
    if multialignment_upload_state_data is None or "maf" not in multialignment_upload_state_data["filename"]:
        return False
    else:
        return True

@app.callback(Output(id_missing_symbol_param, 'is_open'),
              [Input(id_fasta_provider_choice, 'value')])
def toggle_mising_symbol_param(fasta_provider_choice):
    if fasta_provider_choice is None or fasta_provider_choice != "Symbol":
        return False
    else:
        return True

@app.callback(Output(id_fasta_upload_param, 'is_open'),
              [Input(id_fasta_provider_choice, 'value')])
def toggle_fasta_upload_param(fasta_provider_choice):
    if fasta_provider_choice is None or fasta_provider_choice != "File":
        return False
    else:
        return True


# FASTA VALIDATION


@app.callback(Output(id_fasta_upload_state, 'data'),
              [Input(id_fasta_upload, 'contents'),
               Input(id_session_state, 'data')],
              [State(id_fasta_upload, 'filename')])
def validate_fasta_file(file_content, session_state, file_name):
    if file_content is None or file_name is None or session_state is None:
        return None
    else:
        if "zip" in file_name:
            file_content = tools.decode_zip_content(file_content)
        else:
            file_content = tools.decode_content(file_content)
        output_dir = Path(session_state["output_dir"])
        fasta_path = tools.get_child_path(output_dir, file_name)
        if "zip" in file_name:
            tools.save_to_file(file_content, fasta_path, 'wb')
        else:
            tools.save_to_file(file_content, fasta_path)
        error_message = processing.fasta_file_is_valid(fasta_path)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}

@app.callback(Output(id_fasta_upload_state_info, 'children'),
              [Input(id_fasta_upload_state, 'data')])
def show_fasta_validation_result(upload_state_data):
    if upload_state_data is None or len(upload_state_data) == 0:
        return []
    else:
        if upload_state_data["is_correct"]:
            filename = upload_state_data["filename"]
            return get_success_info(f"File {filename} uploaded.")
        else:
            return get_error_info(upload_state_data["error"])

# HANDLE SESSION DIR
@app.callback(Output(id_session_state, 'data'),
              [Input(id_fasta_upload, 'contents')],
              [State(id_session_state, 'data')])
def create_output_dir(_, session_state):
    if session_state is None:
        output_dir = tools.create_output_dir()
        session_state = {"output_dir": str(output_dir)}
    return session_state

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
