import os
import shutil
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Optional
from base64 import b64decode
import pandas as pd
from pangtreebuild.output import PangenomeJSON
import uuid
from io import StringIO

def unjsonify_jsonpangenome(jsonified_pangenome: str) -> PangenomeJSON:
    return PangenomeJSON.str_to_PangenomeJSON(jsonified_pangenome)


def jsonify_builtin_types(data: Any) -> str:
    return json.dumps(data)


def unjsonify_builtin_types(jsonified_data: str) -> Any:
    return json.loads(jsonified_data)


def jsonify_df(df: pd.DataFrame) -> str:
    return df.to_json()


def unjsonify_df(jsonified_df: str) -> pd.DataFrame:
    return pd.read_json(jsonified_df)


def decode_content(content: str) -> str:
    if not content:
        return ''
    content_string = content.split(',')[1]
    return b64decode(content_string).decode('ascii')


def decode_zip_content(content: str) -> str:
    if not content:
        return ''
    content_string = content.split(',')[1]
    return b64decode(content_string)


def create_output_dir() -> Path:
    parent_output_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__)))).joinpath("../../users_temp_data/")
    current_time = get_current_time()
    uid = str(uuid.uuid4()).replace("-", "_")

    output_dir = "_".join([current_time, uid])

    output_dir_path = parent_output_dir.joinpath(output_dir)
    create_dir(output_dir_path)
    return output_dir_path


def get_cwd() -> Path:
    """Returns current working directory."""

    return Path(os.getcwd())


def get_current_time() -> str:
    """Returns current date and time in format MM_DD__HH_MM_SS"""

    return datetime.now().strftime('%m_%d__%H_%M_%S')


def get_child_dir(parent_dir_path: Path, child_dir_name: str) -> Path:
    child_dir_path = get_child_path(parent_dir_path, child_dir_name)
    create_dir(child_dir_path)
    return child_dir_path


def create_dir(dir_path: Path):
        dir_path.mkdir()


def get_child_path(output_dir: Path, file_name: str) -> Path:
    return output_dir.joinpath(file_name)


def save_to_file(filecontent: str, filename: Path, mode: Optional[str] = 'w') -> None:
    """Saves string to file."""

    with open(filename, mode) as output:
        output.write(filecontent)

def read_file_to_stream(path: Path):
    with open(path) as in_file:
        filecontent = in_file.read()
    return StringIO(filecontent)


def dir_to_zip(dir_name: Path) -> Path:
    shutil.make_archive(dir_name, 'zip', dir_name)
    return Path(str(dir_name) + ".zip")


def remove_file(path: Path)-> None:
    os.remove(path)