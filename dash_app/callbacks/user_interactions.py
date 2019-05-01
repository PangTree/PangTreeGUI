import shutil
from io import StringIO
from pathlib import Path
from typing import Dict, List

import jsonpickle

import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from poapangenome.consensus.input_types import Blosum, Hbmin, Stop, P
from poapangenome.datamodel.DataType import DataType
from poapangenome.datamodel.fasta_providers.ConstSymbolProvider import ConstSymbolProvider
from poapangenome.datamodel.fasta_providers.FromFile import FromFile
from poapangenome.datamodel.fasta_providers.FromNCBI import FromNCBI
from poapangenome.datamodel.input_types import Maf, Po, MissingSymbol, MetadataCSV
from poapangenome.output import PangenomeJSON
from poapangenome.output.PangenomeJSON import to_json

from dash_app.components import processing
from ..server import app
from dash.dependencies import Input, Output, State
from ..layout.layout_ids import *
from dash_app.layout import about, tools, package, authors
import json
from ..components import jsontools


@app.callback(
    Output(id_last_clicked_hidden, 'children'),
    [Input(id_pang_button, 'n_clicks'),
     Input(id_load_pangenome_button, 'n_clicks')],
    [State(id_last_clicked_hidden, 'children')]
)
def update_last_clicked_info(pang_n_clicks: int, load_pangenome_n_clicks: int, last_clicked_jsonified: str) -> str:
    new_clicked_info = {"pang": 0, "load": 0, "action": ""}
    if last_clicked_jsonified is None:
        if pang_n_clicks == 1:
            new_clicked_info = {"pang": 1, "load": 0, "action": "pang"}
        if load_pangenome_n_clicks == 1:
            new_clicked_info = {"pang": 0, "load": 1, "action": "load"}
    else:
        last_clicked_info = json.loads(last_clicked_jsonified)
        if pang_n_clicks and last_clicked_info["pang"] == pang_n_clicks - 1:
            new_clicked_info = {"pang": last_clicked_info["pang"]+1,
                               "load": last_clicked_info["load"],
                               "action": "pang"}
        if load_pangenome_n_clicks and last_clicked_info["load"] == load_pangenome_n_clicks - 1:
            new_clicked_info = {"pang": last_clicked_info["pang"],
                               "load": last_clicked_info["load"]+1,
                               "action": "load"}
    return json.dumps(new_clicked_info)

# Usunac poniższe!
# @app.callback(
#     Output(id_pangenome_hidden, 'children'),
#     [Input(id_last_clicked_hidden, 'children')],
#     [State(id_pangenome_upload, 'contents')])
# def call_pang(last_clicked_jsonified: str,
#               pangenome_contents,
#               ) -> str:
#     last_clicked = json.loads(last_clicked_jsonified)
#     if last_clicked["action"] == 'load':
#         return jsontools.decode_content(pangenome_contents)


@app.callback(
    Output(id_pangenome_hidden, 'children'),
    [Input(id_pangenome_upload, 'contents')])
def load_visualisation(pangenome_content: str) -> str:
    if not pangenome_content:
        raise PreventUpdate()
    if pangenome_content.startswith("data:application/json;base64"):
        return jsontools.decode_content(pangenome_content)
    return pangenome_content

@app.callback(Output(id_pangenome_upload, 'contents'),
              [Input(id_go_to_vis_tab, 'n_clicks_timestamp')],
              [State(id_session_state, 'data')])
def load_pang_result_to_visualisation(go_to_vis_timestamp, session_state_data):
    if not go_to_vis_timestamp:
        raise PreventUpdate()
    return session_state_data["jsonpangenome"]

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
        output_dir = jsontools.create_output_dir()
    else:
        output_dir = Path(session_state["output_dir"])

    current_processing_output_dir_name = jsontools.get_child_path(output_dir, jsontools.get_current_time())
    jsontools.create_dir(current_processing_output_dir_name)

    if "maf" in multialignment_filename:
        multialignment = Maf(StringIO(jsontools.decode_content(multialignment_content)), filename=multialignment_filename)
    elif "po" in multialignment_filename:
        multialignment = Po(StringIO(jsontools.decode_content(multialignment_content)), filename=multialignment_filename)
    else:
        session_state["error"] = "Cannot create Poagraph. Only MAF and PO files are supported."
        return session_state

    missing_symbol = MissingSymbol(missing_symbol) if missing_symbol != "" else MissingSymbol()

    fasta_path = None
    if fasta_provider_choice == "ncbi":
        fasta_provider = FromNCBI(use_cache=True)
    elif fasta_provider_choice == "file":
        fasta_path = jsontools.get_child_path(current_processing_output_dir_name, fasta_filename)
        save_mode = "wb" if "zip" in fasta_filename else "w"
        jsontools.save_to_file(fasta_content, fasta_path, save_mode)
        fasta_provider = FromFile(fasta_path)
    else:
        fasta_provider = ConstSymbolProvider(missing_symbol)

    if not blosum_contents:
        blosum_path = processing.get_default_blosum_path()
        blosum_contents = jsontools.read_file_to_stream(blosum_path)
    else:
        blosum_path = jsontools.get_child_path(current_processing_output_dir_name, blosum_filename)
        blosum_contents = jsontools.decode_content(blosum_contents)
        jsontools.save_to_file(blosum_contents, blosum_path)
        blosum_contents = StringIO(blosum_contents)
    blosum = Blosum(blosum_contents, blosum_path, missing_symbol)

    metadata = MetadataCSV(StringIO(jsontools.decode_content(metadata_content)), metadata_filename) if metadata_content else None
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
    current_processing_output_zip = jsontools.dir_to_zip(current_processing_output_dir_name)
    current_processing_short_name = "/".join(str(current_processing_output_zip).split("/")[-2:])
    return {"output_dir": str(output_dir),
            "last_output_zip": current_processing_short_name,
            "jsonpangenome": pangenome_json_str}

# @app.callback(
#     Output(id_pangenome_hidden, 'children'),
#     [Input(id_last_clicked_hidden, 'children')],
#     [State(id_pangenome_upload, 'contents'),
#      State('maf_upload', 'contents'),
#      State('metadata_upload', 'contents'),
#      State('pang_options', 'values'),
#      State('algorithm', 'value'),
#      State('hbmin', 'value'),
#      State('r', 'value'),
#      State('multiplier', 'value'),
#      State('stop', 'value'),
#      State('tree_consensus_options', 'values')
#      ])
# def call_pang(last_clicked_jsonified: str,
#               pangenome_contents,
#               maf_contents,
#               metadata_contents,
#               pang_options_values,
#               consensus_algorithm_value,
#               hbmin_value,
#               r_value,
#               multiplier_value,
#               stop_value,
#               tree_consensus_options_values) -> str:
#     last_clicked = json.loads(last_clicked_jsonified)
#     if last_clicked["action"] == 'load':
#         # pangenome_decoded = decode_content(pangenome_contents)
#         # pangenomejson = jsonpickle.decode(pangenome_decoded)
#         # return get_jsonified_pangenome_from_jsonpangenomefile(pangenome_decoded)
#         return get_jsonified_pangenome_from_jsonpangenomefile(pangenome_contents)
#     elif last_clicked["action"] == "pang":
#         print("Wolam pang")
#         # fasta_option = True if 'FASTA' in pang_options_values else False
#         # re_consensus_value = True if 're_consensus' in tree_consensus_options_values else False
#         # anti_fragmentation_value = True if 'anti_fragmentation' in tree_consensus_options_values else False
#         # no_multiplier_anti_granular = True  # todo
#         # output_path = "" #todo
#         # maf_decoded = decode_content(maf_contents)
#         # metadata_decoded = decode_content(metadata_contents) if metadata_contents else None
#         # params = PangenomeParameters(multialignment_file_content=maf_decoded, multialignment_file_path="",
#         #                              metadata_file_content=metadata_decoded, metadata_file_path="", blosum_file_path="",
#         #                              output_path=output_path, generate_fasta=fasta_option, consensus_type="",
#         #                              hbmin=hbmin_value, search_range=r_value, multiplier=multiplier_value,
#         #                              stop=stop_value, re_consensus=re_consensus_value, raw_maf="",
#         #                              fasta_complementation_option="", missing_base_symbol="", fasta_source_file="",
#         #                              max_cutoff_option="", node_cutoff_option="", verbose=True, quiet=True,
#         #                              email_address="paulina-ph@wp.pl", cache=False, p=1, datatype="", output_po="",
#         #                              output_with_nodes=True)
#         # pangenome = run_pangenome_algorithm(params)
#         # jsonpangenome = get_jsonpangenome_from_pangenome(pangenome, params)
#         # jsonified_pangenome = get_jsonified_pangenome_from_jsonpangenome(jsonpangenome)
#         # pangenome_json_path = save_jsonifiedpangenome_to_file(jsonified_pangenome)
#         # shutil.copy(pangenome_json_path, "download/pangenome.json")
#         jsonified_pangenome = ''
#         return jsonified_pangenome
#     else:
#         return ""


# def get_jsonified_pangenome_from_jsonpangenomefile(jsonpangenomefile_stream) -> str:
#     content_type, content_string = jsonpangenomefile_stream.split(',')
#     jsonified_pangenome = b64decode(content_string).decode('ascii')
#     return jsonified_pangenome


def run_pangenome_algorithm() -> str:
    raise NotImplementedError("Run pangenome algorithm")


# def get_jsonpangenome_from_pangenome(pangenome: Pangenome, pangenome_parameters: PangenomeParameters) -> JSONPangenome:
#     return JSONPangenome(pangenome, pangenome_parameters)


# def save_jsonifiedpangenome_to_file(jsonified_pangenome: str) -> Path:
#     raise NotImplementedError("save_jsonifiedpangenome_to_file")
#     jsonpath = Path("") #todo
#     with open(jsonpath, 'w') as json_output:
#         json_output.write(jsonified_pangenome)
#     return jsonpath


def get_jsonified_pangenome_from_jsonpangenome(jsonpangenome: PangenomeJSON.PangenomeJSON) -> str:
    jsonpickle.set_encoder_option('simplejson', indent=4)
    return PangenomeJSON.to_json(jsonpangenome)
    # return jsonpickle.encode(jsonpangenome)


