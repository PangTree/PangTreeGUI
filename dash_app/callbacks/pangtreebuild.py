import io
import os
from io import StringIO
from pathlib import Path
from typing import Dict, List

import dash_html_components as html
import flask
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pangtreebuild.consensus.input_types import Blosum, Hbmin, Stop, P
from pangtreebuild.datamodel.DataType import DataType
from pangtreebuild.datamodel.fasta_providers.ConstSymbolProvider import ConstSymbolProvider
from pangtreebuild.datamodel.fasta_providers.FromFile import FromFile
from pangtreebuild.datamodel.fasta_providers.FromNCBI import FromNCBI
from pangtreebuild.datamodel.input_types import Maf, Po, MissingSymbol, MetadataCSV
from pangtreebuild.output.PangenomeJSON import to_json

from dash_app.components import tools
from dash_app.components import pangtreebuild
from dash_app.layout.layout_ids import *
from dash_app.layout.pages import get_task_description_layout
from dash_app.server import app


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
        error_message = pangtreebuild.metadata_file_is_valid(file_content, file_name)
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
            return get_success_info(f"File {filename} is uploaded.")
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
        error_message = pangtreebuild.multialignment_file_is_valid(file_content, file_name)
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
            return get_success_info(f"File {filename} is uploaded.")
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
               Input(id_session_dir, 'data')],
              [State(id_fasta_upload, 'filename')])
def validate_fasta_file(file_content, session_dir, file_name):
    if file_content is None or file_name is None or session_dir is None:
        return None
    else:
        if "zip" in file_name:
            file_content = tools.decode_zip_content(file_content)
        else:
            file_content = tools.decode_content(file_content)
        output_dir = Path(session_dir)
        fasta_path = tools.get_child_path(output_dir, file_name)
        if "zip" in file_name:
            tools.save_to_file(file_content, fasta_path, 'wb')
        else:
            tools.save_to_file(file_content, fasta_path)
        error_message = pangtreebuild.fasta_file_is_valid(fasta_path)
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
            return get_success_info(f"File {filename} is uploaded.")
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
        blosum_file_content = tools.read_file_to_stream(pangtreebuild.get_default_blosum_path())
        file_source_info = "default BLOSUM file"
    else:
        blosum_file_content = StringIO(tools.decode_content(file_content))
        file_source_info = f"provided BLOSUM file: {file_name}"

    error_message = pangtreebuild.blosum_file_is_valid(blosum_file_content, symbol)
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

@app.callback(Output(id_session_dir, 'data'),
              [Input(id_fasta_upload, 'contents')],
              [State(id_session_dir, 'data')])
def create_output_dir(_, session_dir):
    if session_dir is None:
        output_dir = tools.create_output_dir()
        session_dir = str(output_dir)
    return session_dir

# EXAMPLE DATASETS

@app.callback(
    Output("ebola_collapse", "is_open"),
    [Input("collapse-ebola-button", "n_clicks")],
    [State("ebola_collapse", "is_open")],
)
def toggle_ebola_example_collapse(ebola_btn_clicks, is_open):
    if ebola_btn_clicks:
        return not is_open
    return is_open


@app.callback(
    Output("simulated_collapse", "is_open"),
    [Input("collapse_simulated_button", "n_clicks")],
    [State("simulated_collapse", "is_open")],
)
def toggle_collapse(simulated_btn_clicks, is_open):
    if simulated_btn_clicks:
        return not is_open
    return is_open


# RUN PROCESSING
@app.callback(
    Output(id_session_state, 'data'),
    [Input(id_pang_button, 'n_clicks')],
    [State(id_session_state, 'data'),
     State(id_session_dir, 'data'),
     State(id_data_type, "value"),
     State(id_multialignment_upload, "contents"),
     State(id_multialignment_upload, "filename"),
     State(id_fasta_provider_choice, "value"),
     State(id_fasta_upload, "contents"),
     State(id_fasta_upload, "filename"),
     State(id_missing_symbol_input, "value"),
     State(id_blosum_upload, "contents"),
     State(id_blosum_upload, "filename"),
     State(id_consensus_algorithm_choice, "value"),
     State(id_output_configuration, "values"),
     State(id_metadata_upload, "contents"),
     State(id_metadata_upload, "filename"),
     State(id_hbmin_input, "value"),
     State(id_stop_input, "value"),
     State(id_p_input, "value")],
)
def run_pangenome(run_processing_btn_click,
                  session_state: Dict,
                  session_dir: str,
                  datatype: str,
                  multialignment_content: str,
                  multialignment_filename: str,
                  fasta_provider_choice: str,
                  fasta_content: str,
                  fasta_filename: str,
                  missing_symbol: str,
                  blosum_contents: str,
                  blosum_filename: str,
                  consensus_choice: str,
                  output_config: List[str],
                  metadata_content: str,
                  metadata_filename: str,
                  hbmin_value: float,
                  stop_value: float,
                  p_value: float):
    if run_processing_btn_click == 0:
        raise PreventUpdate()
    if session_state is None:
        session_state = {}
    if session_dir is None:
        session_dir = tools.create_output_dir()
    else:
        session_dir = Path(session_dir)

    current_processing_output_dir_name = tools.get_child_path(session_dir, tools.get_current_time())
    tools.create_dir(current_processing_output_dir_name)

    if "maf" in multialignment_filename:
        multialignment = Maf(StringIO(tools.decode_content(multialignment_content)), filename=multialignment_filename)
    elif "po" in multialignment_filename:
        multialignment = Po(StringIO(tools.decode_content(multialignment_content)), filename=multialignment_filename)
    else:
        session_state["error"] = "Cannot create Poagraph. Only MAF and PO files are supported."
        return session_state

    missing_symbol = MissingSymbol(missing_symbol) if missing_symbol != "" else MissingSymbol()

    fasta_path = None
    if fasta_provider_choice == "NCBI":
        fasta_provider = FromNCBI(use_cache=True)
    elif fasta_provider_choice == "File":
        fasta_path = tools.get_child_path(current_processing_output_dir_name, fasta_filename).resolve()
        save_mode = "wb" if "zip" in fasta_filename else "w"
        if "zip" in fasta_filename:
            fasta_decoded_content = tools.decode_zip_content(fasta_content)
        else:
            fasta_decoded_content = tools.decode_content(fasta_content)
        tools.save_to_file(fasta_decoded_content, fasta_path, save_mode)
        fasta_provider = FromFile(fasta_path)
    else:
        fasta_provider = ConstSymbolProvider(missing_symbol)

    if not blosum_contents:
        blosum_path = pangtreebuild.get_default_blosum_path()
        blosum_contents = tools.read_file_to_stream(blosum_path)
    else:
        blosum_path = tools.get_child_path(current_processing_output_dir_name, blosum_filename)
        blosum_contents = tools.decode_content(blosum_contents)
        tools.save_to_file(blosum_contents, blosum_path)
        blosum_contents = StringIO(blosum_contents)
    blosum = Blosum(blosum_contents, blosum_path)

    metadata = MetadataCSV(StringIO(tools.decode_content(metadata_content)), metadata_filename) if metadata_content else None
    pangenomejson = pangtreebuild.run_pangtreebuild(output_dir=current_processing_output_dir_name,
                                                 datatype=DataType[datatype],
                                                 multialignment=multialignment,
                                                 fasta_provider=fasta_provider,
                                                 blosum=blosum,
                                                 consensus_choice=consensus_choice,
                                                 output_po=True if "po" in output_config else False,
                                                 output_fasta=True if "fasta" in output_config else False,
                                                 missing_symbol=missing_symbol,
                                                 metadata=metadata,
                                                 hbmin=Hbmin(hbmin_value) if hbmin_value else None,
                                                 stop=Stop(stop_value) if stop_value else None,
                                                 p=P(p_value) if p_value else None,
                                                 fasta_path=fasta_filename if fasta_filename else None)
    pangenome_json_str = to_json(pangenomejson)

    current_processing_output_zip = tools.dir_to_zip(current_processing_output_dir_name)
    current_processing_short_name = "/".join(str(current_processing_output_zip).split("/")[-2:])
    return {"last_output_zip": current_processing_short_name,
            "jsonpangenome": pangenome_json_str,
            "error": ""}


# DOWNLOAD RESULTS

@app.callback(Output(id_download_processing_result, "href"),
              [Input(id_session_state, 'data')])
def update_download_result_content(session_state_data):
    if session_state_data is None:
        raise PreventUpdate()
    if not "last_output_zip" in session_state_data:
        return ""
    return f'/export/pang?n={session_state_data["last_output_zip"]}'


@app.server.route('/export/pang')
def export_pang_result_zip():

    zip_short_path = flask.request.args.get('n')
    zip_full_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__)))).joinpath(
        "../../users_temp_data/").joinpath(zip_short_path)

    with open(zip_full_path, 'rb') as f:
        data = io.BytesIO(f.read())
    data.seek(0)

    result_id = zip_short_path.split("/")[1]
    return flask.send_file(
        data,
        mimetype='application/zip',
        attachment_filename=f'result_{result_id}',
        as_attachment=True,
        cache_timeout=0
    )

@app.callback(Output(id_poapangenome_result, "is_open"),
              [Input(id_session_state, 'data')])
def open_poapangenome_result(session_state_data):
    if session_state_data is None or "jsonpangenome" not in session_state_data:
        return False
    return True

@app.callback(Output(id_poapangenome_result_description, "children"),
              [Input(id_session_state, 'data')])
def get_poapangenome_result_description(session_state_data):
    if session_state_data is None or "jsonpangenome" not in session_state_data:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(session_state_data["jsonpangenome"])
    poapangenome_task_description = get_task_description_layout(jsonpangenome)
    return poapangenome_task_description


@app.callback(Output(id_result_icon, "className"),
              [Input(id_session_state, 'data')])
def get_poapangenome_result_description(session_state_data):
    if session_state_data is None or "jsonpangenome" not in session_state_data:
        return ""
    if session_state_data["error"]:
        return "fas fa-times-circle incorrect"
    else:
        return "fas fa-check-circle correct"
