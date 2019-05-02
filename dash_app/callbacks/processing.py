import io
import os

import flask
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
from ..server import app
from ..layout.layout_ids import *
from ..components import tools
from poapangenome.consensus.input_types import Blosum, Hbmin, Stop, P
from poapangenome.datamodel.DataType import DataType
from poapangenome.datamodel.fasta_providers.ConstSymbolProvider import ConstSymbolProvider
from poapangenome.datamodel.fasta_providers.FromFile import FromFile
from poapangenome.datamodel.fasta_providers.FromNCBI import FromNCBI
from poapangenome.datamodel.input_types import Maf, Po, MissingSymbol, MetadataCSV
from poapangenome.output.PangenomeJSON import to_json

from dash_app.components import processing
from io import StringIO
from pathlib import Path
from typing import Dict, List


# RUN POAPANGENOME

@app.callback(
    Output(id_session_state, 'data'),
    [Input(id_pang_button, 'n_clicks_timestamp')],
    [State(id_session_state, 'data'),
     State(id_data_type, "value"),
     State(id_multialignment_upload, "contents"),
     State(id_multialignment_upload, "filename"),
     State(id_fasta_provider_choice, "value"),
     State(id_fasta_upload, "contents"),
     State(id_fasta_upload, "filename"),
     State(id_missing_symbol_input, "value"),
     State(id_blosum_upload, "contents"),
     State(id_blosum_upload, "filename"),
     State(id_tree_algorithm_choice, "value"),
     State(id_output_configuration, "values"),
     State(id_metadata_upload, "contents"),
     State(id_metadata_upload, "filename"),
     State(id_hbmin, "value"),
     State(id_stop, "value"),
     State(id_p, "value")],
)
def run_pangenome(run_processing_btn_click,
                  session_state: Dict,
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
    if "output_dir" not in session_state:
        output_dir = tools.create_output_dir()
    else:
        output_dir = Path(session_state["output_dir"])

    current_processing_output_dir_name = tools.get_child_path(output_dir, tools.get_current_time())
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
    if fasta_provider_choice == "ncbi":
        fasta_provider = FromNCBI(use_cache=True)
    elif fasta_provider_choice == "file":
        fasta_path = tools.get_child_path(current_processing_output_dir_name, fasta_filename)
        save_mode = "wb" if "zip" in fasta_filename else "w"
        tools.save_to_file(fasta_content, fasta_path, save_mode)
        fasta_provider = FromFile(fasta_path)
    else:
        fasta_provider = ConstSymbolProvider(missing_symbol)

    if not blosum_contents:
        blosum_path = processing.get_default_blosum_path()
        blosum_contents = tools.read_file_to_stream(blosum_path)
    else:
        blosum_path = tools.get_child_path(current_processing_output_dir_name, blosum_filename)
        blosum_contents = tools.decode_content(blosum_contents)
        tools.save_to_file(blosum_contents, blosum_path)
        blosum_contents = StringIO(blosum_contents)
    blosum = Blosum(blosum_contents, blosum_path, missing_symbol)

    metadata = MetadataCSV(StringIO(tools.decode_content(metadata_content)), metadata_filename) if metadata_content else None
    pangenomejson = processing.run_poapangenome(output_dir=current_processing_output_dir_name,
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



    #copy all needed file etc. from contents controls to the folder
    # call poapangenome with output as this folder
    # z tego folderu zrobić potem zip
    current_processing_output_zip = tools.dir_to_zip(current_processing_output_dir_name)
    current_processing_short_name = "/".join(str(current_processing_output_zip).split("/")[-2:])
    return {"output_dir": str(output_dir),
            "last_output_zip": current_processing_short_name,
            "jsonpangenome": pangenome_json_str}


# SHOW RESULTS

@app.callback(Output(id_processing_result, "style"),
              [Input(id_session_state, 'data')],
              [State(id_processing_result, "style")])
def show_processing_result(session_state_data, processing_result_style):
    if session_state_data is None or "jsonpangenome" not in session_state_data:
        raise PreventUpdate
    if len(session_state_data["jsonpangenome"]):
        processing_result_style["display"] = "block"
    return processing_result_style


@app.callback(Output("tabs-tools", "value"),
              [Input(id_go_to_vis_tab, "n_clicks_timestamp")])
def jump_to_vis_tab(go_to_vis_tab_click):
    if go_to_vis_tab_click > 0:
        return "vis"
    raise PreventUpdate()


@app.callback(Output(id_processing_result_text, "children"),
              [Input(id_session_state, 'data')])
def show_output_description(session_state_data):
    if session_state_data is None or len(session_state_data) == 0:
        raise PreventUpdate()
    return str(session_state_data["jsonpangenome"])


@app.callback(Output(id_pangenome_upload, 'contents'),
              [Input(id_go_to_vis_tab, 'n_clicks_timestamp')],
              [State(id_session_state, 'data')])
def put_poapangenome_result_to_visualisation(go_to_vis_timestamp, session_state_data):
    if not go_to_vis_timestamp:
        raise PreventUpdate()
    return session_state_data["jsonpangenome"]


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
        attachment_filename=f'result_{result_id}.zip',
        as_attachment=True,
        cache_timeout=0
    )

# FORM VALIDATION

@app.callback(Output(id_multalignment_upload_state, 'data'),
              [Input('multialignment_upload', 'contents')],
              [State('multialignment_upload', 'filename')])
def validate_multialignment(file_content, file_name):
    if file_content is None or file_name is None:
        return None
    else:
        file_content = tools.decode_content(file_content)
        error_message = processing.multialignment_file_is_valid(file_content, file_name)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}


@app.callback(Output(id_maf_specific_params, 'style'),
              [Input(id_multalignment_upload_state, 'data')],
              [State(id_maf_specific_params, 'style')])
def show_maf_specific_params(multialignment_upload_state_data, maf_specific_group_style):
    if multialignment_upload_state_data is None or "maf" not in multialignment_upload_state_data["filename"]:
        raise PreventUpdate()
    else:
        maf_specific_group_style["display"] = "block"
        return maf_specific_group_style


@app.callback(Output(id_multalignment_upload_state_info, 'children'),
              [Input(id_multalignment_upload_state, 'data')])
def show_multiaignment_validation_result(multialignment_upload_state_data):
    if multialignment_upload_state_data is None or len(multialignment_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        if multialignment_upload_state_data["is_correct"]:
            filename = multialignment_upload_state_data["filename"]
            return [html.I(className="fas fa-check-circle correct"), html.P(f"File {filename} uploaded.", style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(multialignment_upload_state_data["error"], style={"display": "inline", "margin-left": "10px"})]


@app.callback(Output(id_multalignment_upload_state_info, 'style'),
              [Input(id_multalignment_upload_state, 'data')],
              [State(id_multalignment_upload_state_info, 'style')])
def show_multialignment(multialignment_upload_state_data, current_style):
    if multialignment_upload_state_data is None or len(multialignment_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        current_style["visibility"] = "visible"
        return current_style


@app.callback(Output(id_fasta_upload_state, 'data'),
              [Input('fasta_upload', 'contents')],
              [State('fasta_upload', 'filename'),
               State(id_session_state, 'data')])
def validate_fasta(file_content, file_name, session_state):
    if file_content is None or file_name is None:
        return None
    else:
        if "zip" in file_name:
            file_content = tools.decode_zip_content(file_content)
        else:
            file_content = tools.decode_content(file_content)

        if session_state is None:
            output_dir = tools.create_output_dir()
            session_state = {"output_dir": output_dir}
        else:
            output_dir = session_state["output_dir"]
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
def show_fasta_validation_result(fasta_upload_state_data):
    if fasta_upload_state_data is None or len(fasta_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        if fasta_upload_state_data["is_correct"]:
            filename = fasta_upload_state_data["filename"]
            return [html.I(className="fas fa-check-circle correct"), html.P(f"File {filename} uploaded.", style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(fasta_upload_state_data["error"], style={"display": "inline", "margin-left": "10px"})]


@app.callback(Output(id_fasta_upload_state_info, 'style'),
              [Input(id_fasta_upload_state, 'data')],
              [State(id_fasta_upload_state_info, 'style')])
def show_fasta_upload_info(fasta_upload_state_data, current_style):
    if fasta_upload_state_data is None or len(fasta_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        current_style["visibility"] = "visible"
        return current_style

@app.callback(Output(id_fasta_upload_param, 'style'),
              [Input(id_fasta_provider_choice, "value")],
              [State(id_fasta_upload_param, 'style')])
def show_fasta_upload(fasta_privider_choice, fasta_upload_style):
    if fasta_privider_choice == "File":
        fasta_upload_style["display"] = "block"
        return fasta_upload_style
    else:
        fasta_upload_style["display"] = "none"
        return fasta_upload_style


@app.callback(Output(id_missing_symbol_param, 'style'),
              [Input(id_fasta_provider_choice, "value")],
              [State(id_missing_symbol_param, 'style')])
def show_fasta_upload(fasta_privider_choice, missing_symbol_param_style):
    if fasta_privider_choice == "Symbol":
        missing_symbol_param_style["display"] = "block"
        return missing_symbol_param_style
    else:
        missing_symbol_param_style["display"] = "none"
        return missing_symbol_param_style


@app.callback(Output(id_hbmin_param, 'style'),
              [Input(id_tree_algorithm_choice, "value")],
              [State(id_hbmin_param, 'style')])
def show_hbmin_param(tree_algorithm_choice, hbmin_param_style):
    if tree_algorithm_choice == "poa":
        hbmin_param_style["display"] = "block"
    else:
        hbmin_param_style["display"] = "none"
    return hbmin_param_style

@app.callback(Output(id_tree_specific_params, 'style'),
              [Input(id_tree_algorithm_choice, "value")],
              [State(id_tree_specific_params, 'style')])
def show_tree_params(tree_algorithm_choice, tree_params_style):
    if tree_algorithm_choice == "tree":
        tree_params_style["display"] = "block"
    else:
        tree_params_style["display"] = "none"
    return tree_params_style

@app.callback(Output(id_hbmin, 'required'),
              [Input(id_tree_algorithm_choice, "value")])
def make_hbmin_required(tree_algorithm_choice):
    if tree_algorithm_choice == "poa":
        return True
    else:
        return False


@app.callback(Output(id_stop, 'required'),
              [Input(id_tree_algorithm_choice, "value")])
def make_stop_required(tree_algorithm_choice):
    if tree_algorithm_choice == "tree":
        return True
    else:
        return False


@app.callback(Output(id_p, 'required'),
              [Input(id_tree_algorithm_choice, "value")])
def make_stop_required(tree_algorithm_choice):
    if tree_algorithm_choice == "tree":
        return True
    else:
        return False


@app.callback(Output(id_blosum_upload_state, 'data'),
              [Input('blosum_upload', 'contents'),
               Input(id_missing_symbol_input, 'value'),
               Input(id_fasta_provider_choice, "value")],
              [State('blosum_upload', 'filename')])
def validate_blosum(file_content, missing_symbol, fasta_provider_choice, file_name):
    if file_content is None and missing_symbol is None:
        return None
    if fasta_provider_choice == "Symbol" and missing_symbol != "":
        symbol = missing_symbol
    else:
        symbol = '?'

    if file_content is None:
        blosum_file_content=tools.read_file_to_stream(processing.get_default_blosum_path())
        file_source_info = "default BLOSUM file"
    else:
        blosum_file_content = StringIO(tools.decode_content(file_content))
        file_source_info = f"provided BLOSUM file: {file_name}"

    error_message = processing.blosum_file_is_valid(blosum_file_content, symbol)
    if len(error_message) == 0:
        validation_message = f"The {file_source_info} is correct and contains symbol for missing nucleotides/proteins: {symbol}."
        return {"is_correct": True, "filename": file_name, "symbol": symbol, "validation_message": validation_message}
    else:
        validation_message = f"Error in {file_source_info} or symbol for missing nucleotides/proteins: {symbol}. Reason: {error_message}"
        return {"is_correct": False, "filename": file_name, "symbol": symbol, "validation_message": validation_message}


@app.callback(Output(id_blosum_upload_state_info, 'children'),
              [Input(id_blosum_upload_state, 'data')])
def show_blosum_validation_result(blosum_upload_state_data):
    if blosum_upload_state_data is None or len(blosum_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        validation_message = blosum_upload_state_data["validation_message"]
        if blosum_upload_state_data["is_correct"]:
            return [html.I(className="fas fa-check-circle correct"), html.P(f"{validation_message}", style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(f"{validation_message}", style={"display": "inline", "margin-left": "10px"})]


@app.callback(Output(id_blosum_upload_state_info, 'style'),
              [Input(id_blosum_upload_state, 'data')],
              [State(id_blosum_upload_state_info, 'style')])
def show_blosum_upload_info(blosum_upload_state_data, current_style):
    if blosum_upload_state_data is None or len(blosum_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        current_style["visibility"] = "visible"
        return current_style


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
            return [html.I(className="fas fa-check-circle correct"), html.P(f"File {filename} uploaded.", style={"display": "inline", "margin-left": "10px"})]
        else:
            return [html.I(className="fas fa-exclamation-circle incorrect"),
                    html.P(metadata_upload_state_data["error"], style={"display": "inline", "margin-left": "10px"})]


@app.callback(Output(id_metadata_upload_state_info, 'style'),
              [Input(id_metadata_upload_state, 'data')],
              [State(id_metadata_upload_state_info, 'style')])
def show_metadata_upload_info(metadata_upload_state_data, current_style):
    if metadata_upload_state_data is None or len(metadata_upload_state_data) == 0:
        raise PreventUpdate()
    else:
        current_style["visibility"] = "visible"
        return current_style

