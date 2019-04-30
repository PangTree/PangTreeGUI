from io import StringIO

# def parse_contents(contents, filename, date):
#     content_type, content_string = contents.split(',')
#
#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename:
#             # Assume that the user uploaded a CSV file
#             df = pd.read_csv(
#                 io.StringIO(decoded.decode('utf-8')))
#         elif 'xls' in filename:
#             # Assume that the user uploaded an excel file
#             df = pd.read_excel(io.BytesIO(decoded))
#     except Exception as e:
#         print(e)
#         return html.Div([
#             'There was an error processing this file.'
#         ])
#
#     return html.Div([
#         html.H5(filename),
#         html.H6(datetime.datetime.fromtimestamp(date)),
#
#         dash_table.DataTable(
#             data=df.to_dict('records'),
#             columns=[{'name': i, 'id': i} for i in df.columns]
#         ),
#
#         html.Hr(),  # horizontal line
#
#         # For debugging, display the raw contents provided by the web browser
#         html.Div('Raw Content'),
#         html.Pre(contents[0:200] + '...', style={
#             'whiteSpace': 'pre-wrap',
#             'wordBreak': 'break-all'
#         })
#     ])
from pathlib import Path

from poapangenome.datamodel.fasta_providers.FastaProvider import FastaProviderException
from poapangenome.datamodel.fasta_providers.FromFile import FromFile
from poapangenome.datamodel.input_types import Maf, InputError, Po


def multialignment_file_is_valid(multialignment_content: str, filename: str) -> str:
    if "maf" in filename:
        try:
            m = Maf(StringIO(multialignment_content), filename=filename)
        except InputError as e:
            return str(e)
    elif "po" in filename:
        try:
            m = Po(StringIO(multialignment_content), filename=filename)
        except InputError as e:
            return str(e)
    else:
        return "Only po and maf file are accepted. The extension must be present in filename."
    return ""


def fasta_file_is_valid(fasta_path: Path) -> str:
    try:
        _ = FromFile(fasta_path)
    except FastaProviderException as e:
        return str(e)
    return ""
