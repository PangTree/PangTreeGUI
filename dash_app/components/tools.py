import os
import shutil
import uuid
import base64
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

from pangtreebuild.serialization.json import PangenomeJSON, str_to_PangenomeJSON


def unjsonify_jsonpangenome(jsonified_pangenome: str) -> PangenomeJSON:
    return str_to_PangenomeJSON(jsonified_pangenome)


# def jsonify_builtin_types(data: Any) -> str:
#     return json.dumps(data)
#
#
# def unjsonify_builtin_types(jsonified_data: str) -> Any:
#     return json.loads(jsonified_data)
#
#
# def jsonify_df(df: pd.DataFrame) -> str:
#     return df.to_json()
#
#
# def unjsonify_df(jsonified_df: str) -> pd.DataFrame:
#     return pd.read_json(jsonified_df)


def encode_content(content: str) -> str:
    encoded = base64.b64encode(content.encode('ascii'))
    return "data:text/csv;base64,"+str(encoded)[2:-1]


def decode_content(content: str) -> str:
    if not content:
        return ''
    content_string = content.split(',')[1]
    return base64.b64decode(content_string).decode('ascii')


def decode_zip_content(content: str) -> str:
    if not content:
        return ''
    content_string = content.split(',')[1]
    return base64.b64decode(content_string)


def create_output_dir() -> Path:
    parent_output_dir = Path(os.path.abspath(os.path.join(
        os.path.dirname(__file__)))).joinpath("../../users_temp_data/")
    if not parent_output_dir.exists():
        create_dir(parent_output_dir)
    current_time = get_current_time()
    uid = str(uuid.uuid4()).replace("-", "_")

    output_dir = "_".join([current_time, uid])

    output_dir_path = parent_output_dir.joinpath(output_dir)
    create_dir(output_dir_path)
    return output_dir_path


def get_current_time() -> str:
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


def remove_file(path: Path) -> None:
    os.remove(path)
