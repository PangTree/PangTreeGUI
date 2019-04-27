import json
from typing import Dict, Union, Any

import jsonpickle
import pandas as pd
from poapangenome.output import PangenomeJSON


def unjsonify_jsonpangenome(jsonified_pangenome: str) -> PangenomeJSON:
    # return jsonpickle.decode(jsonified_pangenome)
    return PangenomeJSON.str_to_PangenomeJSON(jsonified_pangenome)


def jsonify_builtin_types(data: Any) -> str:
    return json.dumps(data)


def unjsonify_builtin_types(jsonified_data: str) -> Any:
    return json.loads(jsonified_data)


def jsonify_df(df: pd.DataFrame) -> str:
    return df.to_json()


def unjsonify_df(jsonified_df: str) -> pd.DataFrame:
    return pd.read_json(jsonified_df)
