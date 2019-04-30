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
        return None
    else:
        file_content = jsontools.decode_content(file_content)
        error_message = processing.multialignment_file_is_valid(file_content, file_name)
        if len(error_message) == 0:
            return {"is_correct": True, "filename": file_name, "error": error_message}
        else:
            return {"is_correct": False, "filename": file_name, "error": error_message}


@app.callback(Output(id_maf_specific_params, 'style'),
              [Input(id_multalignment_upload_state, 'data')],
              [State(id_maf_specific_params, 'style')])
def validate_multialignment(multialignment_upload_state_data, maf_specific_group_style):
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
def validate_multialignment(multialignment_upload_state_data, current_style):
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
            file_content = jsontools.decode_zip_content(file_content)
        else:
            file_content = jsontools.decode_content(file_content)

        if session_state is None:
            output_dir = jsontools.create_output_dir()
            session_state = {"output_dir": output_dir}
        else:
            output_dir = session_state["output_dir"]
        fasta_path = jsontools.get_child_path(output_dir, file_name)
        if "zip" in file_name:
            jsontools.save_to_file(file_content, fasta_path, 'wb')
        else:
            jsontools.save_to_file(file_content, fasta_path)
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
def update_fasta_upload_info(fasta_upload_state_data, current_style):
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
