import os
from io import StringIO
from typing import Union, Optional

import dash_html_components as html

from pangtreebuild.consensus import simple_tree_generator, tree_generator
from pangtreebuild.consensus.cutoffs import MAX2, NODE3
from pangtreebuild.datamodel.DataType import DataType
from pangtreebuild.datamodel.Poagraph import Poagraph
from pangtreebuild.datamodel.fasta_providers.ConstSymbolProvider import ConstSymbolProvider
from pangtreebuild.datamodel.fasta_providers.FromNCBI import FromNCBI
from pangtreebuild.output.PangenomeFASTA import poagraph_to_fasta, consensuses_tree_to_fasta
from pangtreebuild.output.PangenomeJSON import to_PangenomeJSON, to_json, PangenomeJSON, TaskParameters
from pangtreebuild.output.PangenomePO import poagraph_to_PangenomePO
from pangtreebuild.tools import logprocess

from dash_app.components import tools
import time

from pathlib import Path

from pangtreebuild.consensus.input_types import Blosum, ConsensusInputError, Hbmin, Stop, P
from pangtreebuild.datamodel.fasta_providers.FastaProvider import FastaProviderException
from pangtreebuild.datamodel.fasta_providers.FromFile import FromFile
from pangtreebuild.datamodel.input_types import Maf, InputError, Po, MissingSymbol, MetadataCSV


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
        blosum = Blosum(file_content, None)
        if missing_symbol != None:
            blosum.check_if_symbol_is_present(missing_symbol)
    except ConsensusInputError as e:
        return str(e)
    return ""

def metadata_file_is_valid(file_content: str, file_path: Path) -> str:
    try:
        _ = MetadataCSV(StringIO(file_content), file_path)
    except InputError as e:
        return str(e)
    return ""


def get_default_blosum_path():
    parent_dir = Path(os.path.dirname(os.path.abspath(__file__)) + '/')
    return tools.get_child_path(parent_dir, "../dependencies/blosum80.mat")


def run_pangtreebuild(output_dir: Path,
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
    logprocess.remove_console_handler_from_root_logger()
    poagraph, dagmaf = None, None
    if isinstance(multialignment, Maf):
        poagraph, dagmaf = Poagraph.build_from_dagmaf(multialignment, fasta_provider, metadata)
    elif isinstance(multialignment, Po):
        poagraph = Poagraph.build_from_po(multialignment, metadata)

    consensus_output_dir = tools.get_child_dir(output_dir, "consensus")
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
        tools.save_to_file(pangenome_po, tools.get_child_path(output_dir, "poagraph.po"))

    if output_fasta:
        sequences_fasta = poagraph_to_fasta(poagraph)
        tools.save_to_file(sequences_fasta, tools.get_child_path(output_dir, "sequences.fasta"))
        if consensus_tree:
            consensuses_fasta = consensuses_tree_to_fasta(poagraph, consensus_tree)
            tools.save_to_file(consensuses_fasta, tools.get_child_path(output_dir, "consensuses.fasta"))

    end = time.time()

    task_parameters = TaskParameters(running_time=f"{end - start}s",
                                     multialignment_file_path=multialignment.filename,
                                     multialignment_format=str(type(multialignment).__name__),
                                     datatype=datatype.name,
                                     metadata_file_path=metadata.filename if metadata else None,
                                     blosum_file_path=blosum.filepath.name,
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
    tools.save_to_file(pangenome_json_str, tools.get_child_path(output_dir, "pangenome.json"))
    return pangenomejson


