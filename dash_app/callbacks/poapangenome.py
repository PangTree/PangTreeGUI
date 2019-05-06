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


# Blosum Validation

@app.callback(Output(id_blosum_upload_state, 'data'),
              [Input(id_blosum_upload, 'contents'),
               Input(id_missing_symbol_input, 'value'),
               Input(id_fasta_provider_choice, "value")],
              [State(id_blosum_upload, 'filename')])
def validate_blosum_file(file_content, missing_symbol, fasta_provider_choice, file_name):
    if file_content is None or file_name is None:
        return None

    if fasta_provider_choice == "Symbol" and missing_symbol != "":
        symbol = missing_symbol
    else:
        symbol = None

    if file_content is None:
        blosum_file_content = tools.read_file_to_stream(processing.get_default_blosum_path())
        file_source_info = "default BLOSUM file"
    else:
        blosum_file_content = StringIO(tools.decode_content(file_content))
        file_source_info = f"provided BLOSUM file: {file_name}"

    error_message = processing.blosum_file_is_valid(blosum_file_content, symbol)
    if len(error_message) == 0:
        symbol_info = f"It contains symbol for missing nucleotides/proteins: {symbol}." if symbol else ""
        validation_message = f"The {file_source_info} is correct. " + symbol_info
        return {"is_correct": True,
                "filename": file_name,
                "symbol": symbol,
                "validation_message": validation_message}
    else:
        validation_message = f"Error in {file_source_info} or symbol for missing nucleotides/proteins: {symbol}. " \
            f"Reason: {error_message}"
        return {"is_correct": False,
                "filename": file_name,
                "symbol": symbol,
                "validation_message": validation_message}


@app.callback(Output(id_blosum_upload_state_info, 'children'),
              [Input(id_blosum_upload_state, 'data')])
def show_validation_result(blosum_upload_state_data):
    if blosum_upload_state_data is None or len(blosum_upload_state_data) == 0:
        return []
    else:
        validation_message = blosum_upload_state_data["validation_message"]
        if blosum_upload_state_data["is_correct"]:
            return [html.I(className="fas fa-check-circle correct"),
                    html.P(f"{validation_message}", style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(f"{validation_message}", style={"display": "inline", "margin-left": "10px"})]

# POA specific parameters toggling

@app.callback(Output(id_poa_specific_params, 'is_open'),
              [Input(id_consensus_algorithm_choice, 'value')])
def toggle_poa_specific_params(consensus_algorithm_choice):
    if consensus_algorithm_choice is None or consensus_algorithm_choice != "poa":
        return False
    else:
        return True

# TREE specific parameters toggling

@app.callback(Output(id_tree_specific_params, 'is_open'),
              [Input(id_consensus_algorithm_choice, 'value')])
def toggle_tree_specific_params(consensus_algorithm_choice):
    if consensus_algorithm_choice is None or consensus_algorithm_choice != "tree":
        return False
    else:
        return True

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
