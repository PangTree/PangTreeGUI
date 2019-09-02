import dash_html_components as html
from dash.exceptions import PreventUpdate
from pangtreebuild.output.PangenomeJSON import TaskParameters, PangenomeJSON
from ..components import tools
import os
from pathlib import Path


def get_task_params(task_parameters: TaskParameters):
    return [html.H3("Task Parameters", style={"padding-bottom": '10px'}),
        html.P(f"Running time: {task_parameters.running_time}"),
            html.P(f"Input: {task_parameters.multialignment_file_path}")]


def read_pangenome_upload(upload_content) -> PangenomeJSON:
    if not upload_content:
        raise PreventUpdate()
    if upload_content.startswith("data:application/json;base64"):
        jsonified_pangenome = tools.decode_content(upload_content)
    else:
        jsonified_pangenome = upload_content
    return tools.unjsonify_jsonpangenome(jsonified_pangenome)


def get_hash(pangenome_upload_contents) -> int:
    return hash(pangenome_upload_contents)


def get_elem_cache_info(pangenome_hash: int) -> Path:
    cache_file_name = str(abs(pangenome_hash)) + ".pickle"
    parent_output_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__)))).joinpath("../cache/").resolve()
    poagraph_elements_cache_path = tools.get_child_path(parent_output_dir, cache_file_name)
    return poagraph_elements_cache_path


