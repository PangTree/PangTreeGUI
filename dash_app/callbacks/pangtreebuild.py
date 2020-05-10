import io
import os
import base64
from io import StringIO
from pathlib import Path
from typing import Dict, List

import dash
import dash_html_components as html
import flask
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pangtreebuild.affinity_tree.parameters import Blosum, Hbmin, Stop, P
from pangtreebuild.pangenome.graph import DataType
from pangtreebuild.pangenome.parameters.missings import FromFile, FromNCBI, MissingBase
from pangtreebuild.pangenome.parameters.msa import Maf, Po, MetadataCSV
from pangtreebuild.serialization.json import to_json

from dash_app.components import pangtreebuild, tools
from dash_app.layout.pages import get_task_description_layout
from dash_app.server import app


def get_success_info(message):
    return [html.I(className="fas fa-check-circle correct"),
            html.P(message, style={"display": "inline", "margin-left": "10px"})]


def get_error_info(message):
    return [html.I(className="fas fa-exclamation-circle incorrect"),
            html.P(message, style={"display": "inline", "margin-left": "10px"})]


@app.callback([Output("data_type", 'value'),
               Output("metadata_upload", 'filename'), 
               Output("metadata_upload", 'contents'),
               Output("multialignment_upload", 'filename'), 
               Output("multialignment_upload", 'contents'),
               Output("fasta_provider_choice", "value"),
               Output("fasta_upload", 'filename'),
               Output("fasta_upload", 'contents')],
              [Input("use-toy-button", 'n_clicks'),
               Input("use-ebola_subset-button", 'n_clicks'),
               Input("use-ebola-button", 'n_clicks')])
def get_example(toy_n_clicks, ebola_subset_n_clicks, ebola_n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "toy" in changed_id:
        example_folder = "toy_example"
        metadata_file = "metadata.csv"
        multialignment_file = "f.maf"
        fasta_file = "sequence.fasta"
    elif "ebola_subset" in changed_id:
        example_folder = "ebola_subset"
        metadata_file = "metadata.csv"
        multialignment_file = "multialignment.maf"
        fasta_file = None
    elif "ebola" in changed_id:
        example_folder = "ebola"
        metadata_file = "metadata.csv"
        multialignment_file = "multialignment.maf"
        fasta_file = None
    
    with open(f"example_data/pangtreebuild/{example_folder}/{metadata_file}") as f:
        metadata_content = tools.encode_content(f.read())
    with open(f"example_data/pangtreebuild/{example_folder}/{multialignment_file}") as f:
        multialignment_content = tools.encode_content(f.read())
    if fasta_file:
        fasta_provider_choice = "File"
        with open(f"example_data/pangtreebuild/{example_folder}/{fasta_file}") as f:
            fasta_content = tools.encode_content(f.read())
    else:
        fasta_provider_choice = "NCBI"
        fasta_content = None
        
    return "Nucleotides", metadata_file, metadata_content, multialignment_file, multialignment_content, fasta_provider_choice, fasta_file, fasta_content
    

# Metadata Validation

@app.callback(Output("metadata_upload_state", 'data'),
              [Input("metadata_upload", 'contents')],
              [State("metadata_upload", 'filename')])
def validate_metadata_file(file_content, file_name):
    if file_content is None or file_name is None:
        return None
    file_content = tools.decode_content(file_content)
    error_message = pangtreebuild.metadata_file_is_valid(file_content, file_name)
    is_file_correct = True if len(error_message) == 0 else False
    return {"is_correct": is_file_correct, "filename": file_name, "error": error_message}


@app.callback(Output("metadata_upload_state_info", 'children'),
              [Input("metadata_upload_state", 'data')])
def show_validation_result(upload_state_data):
    if upload_state_data is None or len(upload_state_data) == 0:
        return get_error_info("")
    if upload_state_data["is_correct"]:
        filename = upload_state_data["filename"]
        return get_success_info(f"File {filename} is uploaded.")
    return get_error_info(upload_state_data["error"])

# Multialignment validation

@app.callback(Output("multialignment_upload_state", 'data'),
              [Input("multialignment_upload", 'contents')],
              [State("multialignment_upload", 'filename')])
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


@app.callback(Output("multialignment_upload_state_info", 'children'),
              [Input("multialignment_upload_state", 'data')])
def show_multialignment_validation_result(upload_state_data):
    if upload_state_data is None or len(upload_state_data) == 0:
        return get_error_info("")
    else:
        if upload_state_data["is_correct"]:
            filename = upload_state_data["filename"]
            return get_success_info(f"File {filename} is uploaded.")
        else:
            return get_error_info(upload_state_data["error"])

# MAF specific parameters toggling

@app.callback(Output("maf_specific_params", 'is_open'),
              [Input("multialignment_upload_state", 'data')])
def toggle_maf_specific_params(multialignment_upload_state_data):
    if multialignment_upload_state_data and "maf" in multialignment_upload_state_data["filename"]:
        return True
    return False


@app.callback([Output("missing_symbol_param", 'is_open'),
               Output("fasta_upload_param", 'is_open')],
              [Input("fasta_provider_choice", 'value')])
def toggle_mising_symbol_param(fasta_provider_choice):
    return fasta_provider_choice == "Symbol", fasta_provider_choice == "File"

# FASTA VALIDATION

@app.callback(Output("fasta_upload_state", 'data'),
              [Input("fasta_upload", 'contents'),
               Input("session_dir", 'data')],
              [State("fasta_upload", 'filename')])
def validate_fasta_file(file_content, session_dir, file_name):
    if file_content is None or file_name is None or session_dir is None:
        return None
    else:
        if ".zip" in file_name:
            file_content = tools.decode_zip_content(file_content)
        else:
            file_content = tools.decode_content(file_content)
        output_dir = Path(session_dir)
        fasta_path = tools.get_child_path(output_dir, file_name)
        if ".zip" in file_name:
            tools.save_to_file(file_content, fasta_path, 'wb')
        else:
            tools.save_to_file(file_content, fasta_path)
        error_message = pangtreebuild.fasta_file_is_valid(fasta_path)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}


@app.callback(Output("fasta_upload_state_info", 'children'),
              [Input("fasta_upload_state", 'data')])
def show_fasta_validation_result(upload_state_data):
    if upload_state_data is None or len(upload_state_data) == 0:
        return get_error_info("")
    else:
        if upload_state_data["is_correct"]:
            filename = upload_state_data["filename"]
            return get_success_info(f"File {filename} is uploaded.")
        else:
            return get_error_info(upload_state_data["error"])


@app.callback(Output("blosum_upload_state_info", 'children'),
              [Input("blosum_upload_state", 'data')])
def show_validation_result(blosum_upload_state_data):
    if blosum_upload_state_data is None or len(blosum_upload_state_data) == 0:
        return get_success_info("")
    else:
        validation_message = blosum_upload_state_data["validation_message"]
        if blosum_upload_state_data["is_correct"]:
            return [html.I(className="fas fa-check-circle correct"),
                    html.P(f"{validation_message}",
                           style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(f"{validation_message}",
                           style={"display": "inline", "margin-left": "10px"})]


@app.callback([Output("poa_specific_params", 'is_open'),
               Output("tree_specific_params", 'is_open')],
              [Input("consensus_algorithm_choice", 'value')])
def consensus_specific_params(consensus_algorithm_choice):
    return consensus_algorithm_choice == "poa", consensus_algorithm_choice == "tree"


@app.callback(Output("session_dir", 'data'),
              [Input("fasta_upload", 'contents')],
              [State("session_dir", 'data')])
def create_output_dir(_, session_dir):
    if session_dir is None:
        output_dir = tools.create_output_dir()
        session_dir = str(output_dir)
    return session_dir


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
    Output("toy_example_collapse", "is_open"),
    [Input("collapse-toy-example-button", "n_clicks")],
    [State("toy_example_collapse", "is_open")],
)
def toggle_ebola_example_collapse(toy_example_btn_clicks, is_open):
    if toy_example_btn_clicks:
        return not is_open
    return is_open


@app.callback(
    Output("session_state", 'data'),
    [Input("pang_button", 'n_clicks')],
    [State("session_state", 'data'),
     State("session_dir", 'data'),
     State("data_type", "value"),
     State("multialignment_upload", "contents"),
     State("multialignment_upload", "filename"),
     State("fasta_provider_choice", "value"),
     State("fasta_upload", "contents"),
     State("fasta_upload", "filename"),
     State("missing_symbol_input", "value"),
    #  State("blosum_upload", "contents"),
    #  State("blosum_upload", "filename"),
     State("consensus_algorithm_choice", "value"),
     State("output_configuration", "value"),
     State("metadata_upload", "contents"),
     State("metadata_upload", "filename"),
     State("hbmin_input", "value"),
     State("stop_input", "value"),
     State("p_input", "value")],
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

    if multialignment_filename and "maf" in multialignment_filename:
        multialignment = Maf(StringIO(tools.decode_content(multialignment_content)),
                             file_name=multialignment_filename)
    elif multialignment_filename and "po" in multialignment_filename:
        multialignment = Po(StringIO(tools.decode_content(multialignment_content)),
                            file_name=multialignment_filename)
    else:
        session_state["error"] = "Cannot create Poagraph. Only MAF and PO files are supported."
        return session_state

    missing_symbol = MissingBase(missing_symbol) if missing_symbol != "" else MissingBase()

    fasta_path = None
    if fasta_provider_choice == "NCBI":
        fasta_provider = FromNCBI(use_cache=True)
    elif fasta_provider_choice == "File":
        fasta_path = tools.get_child_path(current_processing_output_dir_name,
                                          fasta_filename).resolve()
        save_mode = "wb" if "zip" in fasta_filename else "w"
        if "zip" in fasta_filename:
            fasta_decoded_content = tools.decode_zip_content(fasta_content)
        else:
            fasta_decoded_content = tools.decode_content(fasta_content)
        tools.save_to_file(fasta_decoded_content, fasta_path, save_mode)
        fasta_provider = FromFile(fasta_path)
    blosum_path = pangtreebuild.get_default_blosum_path()
    blosum_contents = tools.read_file_to_stream(blosum_path)
    blosum = Blosum(blosum_contents, blosum_path)

    metadata = MetadataCSV(StringIO(tools.decode_content(metadata_content)),
                           metadata_filename) if metadata_content else None
    pangenomejson = pangtreebuild.run_pangtreebuild(
        output_dir=current_processing_output_dir_name,
        datatype=DataType[datatype],
        multialignment=multialignment,
        fasta_provider=fasta_provider,
        blosum=blosum,
        consensus_choice=consensus_choice,
        output_po=True if "po" in output_config else False,
        output_fasta=True if "fasta" in output_config else False,
        output_newick=True if "newick" in output_config else False,
        missing_symbol=missing_symbol,
        metadata=metadata,
        hbmin=Hbmin(hbmin_value) if hbmin_value else None,
        stop=Stop(stop_value) if stop_value else None,
        p=P(p_value) if p_value else None,
        fasta_path=fasta_filename if fasta_filename else None,
        include_nodes=True # if "nodes" in output_config else False
        )
    pangenome_json_str = to_json(pangenomejson)

    current_processing_output_zip = tools.dir_to_zip(current_processing_output_dir_name)
    current_processing_short_name = "/".join(str(current_processing_output_zip).split("/")[-2:])
    return {"last_output_zip": current_processing_short_name,
            "jsonpangenome": pangenome_json_str,
            "error": ""}


@app.callback(Output("download_processing_result", "href"),
              [Input("session_state", 'data')])
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


@app.callback(Output("poapangenome_result", "is_open"),
              [Input("session_state", 'data')])
def open_poapangenome_result(session_state_data):
    if session_state_data is None or "jsonpangenome" not in session_state_data:
        return False
    return True


@app.callback(Output("poapangenome_result_description", "children"),
              [Input("session_state", 'data')])
def get_poapangenome_result_description(session_state_data):
    if session_state_data is None or "jsonpangenome" not in session_state_data:
        return []
    jsonpangenome = tools.unjsonify_jsonpangenome(session_state_data["jsonpangenome"])
    poapangenome_task_description = get_task_description_layout(jsonpangenome)
    return poapangenome_task_description


@app.callback(Output("result_icon", "className"),
              [Input("session_state", 'data')])
def get_poapangenome_result_description(session_state_data):
    if session_state_data is None or "jsonpangenome" not in session_state_data:
        return ""
    if session_state_data["error"]:
        return "fas fa-times-circle incorrect"
    else:
        return "fas fa-check-circle correct"
