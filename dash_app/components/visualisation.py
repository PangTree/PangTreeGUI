import dash_html_components as html
from poapangenome.output.PangenomeJSON import TaskParameters


def get_task_params(task_parameters: TaskParameters):
    return [html.H3("Task Parameters", style={"padding-bottom": '10px'}),
        html.P(f"Running time: {task_parameters.running_time}"),
            html.P(f"Input: {task_parameters.multialignment_file_path}")]


def get_input_info(jsonpangenome):
    return [html.H3("Input Info"), html.P("Coś o inpucie")]