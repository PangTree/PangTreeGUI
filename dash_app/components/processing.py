import os
from io import StringIO
from typing import Union, Optional

from poapangenome.consensus import simple_tree_generator, tree_generator
from poapangenome.consensus.cutoffs import MAX2, NODE3
from poapangenome.datamodel.DataType import DataType
from poapangenome.datamodel.Poagraph import Poagraph
from poapangenome.datamodel.fasta_providers.ConstSymbolProvider import ConstSymbolProvider
from poapangenome.datamodel.fasta_providers.FromNCBI import FromNCBI
from poapangenome.output.PangenomeFASTA import poagraph_to_fasta, consensuses_tree_to_fasta
from poapangenome.output.PangenomeJSON import to_PangenomeJSON, to_json, PangenomeJSON, TaskParameters
from poapangenome.output.PangenomePO import poagraph_to_PangenomePO
from poapangenome.tools import logprocess

from . import jsontools
import time

from pathlib import Path

from poapangenome.consensus.input_types import Blosum, ConsensusInputError, Hbmin, Stop, P
from poapangenome.datamodel.fasta_providers.FastaProvider import FastaProviderException
from poapangenome.datamodel.fasta_providers.FromFile import FromFile
from poapangenome.datamodel.input_types import Maf, InputError, Po, MissingSymbol, MetadataCSV


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


def blosum_file_is_valid(file_content: Path, missing_symbol: str) -> str:
    try:
        _ = Blosum(file_content, None, MissingSymbol(missing_symbol))
    except ConsensusInputError as e:
        return str(e)
    return ""

def metadata_file_is_valid(file_content: Path) -> str:
    try:
        _ = MetadataCSV(file_content, None)
    except InputError as e:
        return str(e)
    return ""


def get_default_blosum_path():
    parent_dir = Path(os.path.dirname(os.path.abspath(__file__)) + '/')
    return jsontools.get_child_path(parent_dir, "../dependencies/blosum80.mat")


def run_poapangenome(output_dir: Path,
                     datatype: DataType,
                     multialignment: Union[Maf, Po],
                     fasta_provider: Union[FromFile, FromNCBI, ConstSymbolProvider],
                     blosum: Blosum,
                     consensus_choice: str,
                     output_po: bool,
                     output_fasta: bool,
                     missing_symbol: MissingSymbol,
                     metadata: Optional[MetadataCSV]=None,
                     hbmin: Optional[Hbmin] = None,
                     stop: Optional[Stop] = None,
                     p: Optional[P] = None,
                     fasta_path: Optional[Path] = None
                     ) -> PangenomeJSON:
    start = time.time()
    logprocess.add_file_handler_to_logger(output_dir, "details", "details.log", propagate=False)
    logprocess.add_file_handler_to_logger(output_dir, "", "details.log", propagate=False)

    poagraph, dagmaf = None, None
    if isinstance(multialignment, Maf):
        poagraph, dagmaf = Poagraph.build_from_dagmaf(multialignment, fasta_provider, metadata)
    elif isinstance(multialignment, Po):
        poagraph = Poagraph.build_from_po(multialignment, metadata)

    consensus_output_dir = jsontools.get_child_dir(output_dir, "consensus")
    consensus_tree = None
    if consensus_choice == 'poa':
        consensus_tree = simple_tree_generator.get_simple_consensus_tree(poagraph,
                                                                         blosum,
                                                                         consensus_output_dir,
                                                                         hbmin,
                                                                         True)
    elif consensus_choice == 'tree':
        consensus_tree = tree_generator.get_consensus_tree(poagraph,
                                                           blosum,
                                                           consensus_output_dir,
                                                           stop,
                                                           p,
                                                           MAX2(),
                                                           NODE3(),
                                                           True)

    if output_po:
        pangenome_po = poagraph_to_PangenomePO(poagraph)
        jsontools.save_to_file(pangenome_po, jsontools.get_child_path(output_dir, "poagraph.po"))

    if output_fasta:
        sequences_fasta = poagraph_to_fasta(poagraph)
        jsontools.save_to_file(sequences_fasta, jsontools.get_child_path(output_dir, "sequences.fasta"))
        if consensus_tree:
            consensuses_fasta = consensuses_tree_to_fasta(poagraph, consensus_tree)
            jsontools.save_to_file(consensuses_fasta, jsontools.get_child_path(output_dir, "consensuses.fasta"))

    end = time.time()

    task_parameters = TaskParameters(running_time=f"{end - start}s",
                                     multialignment_file_path=multialignment.filename,
                                     multialignment_format=str(type(multialignment).__name__),
                                     datatype=datatype.name,
                                     metadata_file_path=metadata.filename if metadata else None,
                                     blosum_file_path=blosum.filepath,
                                     output_path=None,
                                     output_po=output_po,
                                     output_fasta=output_fasta,
                                     output_with_nodes=True,
                                     verbose=True,
                                     raw_maf=False,
                                     fasta_provider=str(type(fasta_provider).__name__),
                                     missing_base_symbol=missing_symbol.value,
                                     fasta_source_file=fasta_path,
                                     consensus_type=consensus_choice,
                                     hbmin=hbmin.value if hbmin else None,
                                     max_cutoff_option="MAX2",
                                     search_range=None,
                                     node_cutoff_option="NODE3",
                                     multiplier=None,
                                     stop=stop.value if stop else None,
                                     p=p.value if p else None)

    pangenomejson = to_PangenomeJSON(task_parameters=task_parameters,
                                     poagraph=poagraph,
                                     dagmaf=dagmaf,
                                     consensuses_tree=consensus_tree)
    pangenome_json_str = to_json(pangenomejson)
    jsontools.save_to_file(pangenome_json_str, jsontools.get_child_path(output_dir, "pangenome.json"))
    return pangenomejson