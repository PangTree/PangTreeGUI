import os
from io import StringIO
from pathlib import Path
import time
from typing import Union, Optional

from pangtreebuild.affinity_tree.builders import build_poa_affinity_tree, build_affinity_tree
from pangtreebuild.affinity_tree.parameters import Blosum, Hbmin, Stop, P
from pangtreebuild.pangenome.graph import DataType, Poagraph
from pangtreebuild.pangenome import builder
from pangtreebuild.pangenome.parameters.msa import Maf, Po, MetadataCSV
from pangtreebuild.pangenome.parameters.missings import ConstBaseProvider, FromNCBI, FromFile, FastaProviderException, MissingBase
from pangtreebuild.serialization.fasta import poagraph_to_fasta, affinity_tree_to_fasta
from pangtreebuild.serialization.json import to_PangenomeJSON, to_json, PangenomeJSON, TaskParameters
from pangtreebuild.serialization.po import poagraph_to_PangenomePO
from pangtreebuild.tools import logprocess

from dash_app.components import tools


def multialignment_file_is_valid(multialignment_content: str, filename: str) -> str:
    if "maf" in filename:
        try:
            m = Maf(StringIO(multialignment_content), file_name=filename)
        except ValueError as e:
            return str(e)
    elif "po" in filename:
        try:
            m = Po(StringIO(multialignment_content), file_name=filename)
        except ValueError as e:
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
    except ValueError as e:
        return str(e)
    return ""

def metadata_file_is_valid(file_content: str, file_path: Path) -> str:
    try:
        _ = MetadataCSV(StringIO(file_content), file_path)
    except ValueError as e:
        return str(e)
    return ""


def get_default_blosum_path():
    parent_dir = Path(os.path.dirname(os.path.abspath(__file__)) + '/')
    return tools.get_child_path(parent_dir, "../dependencies/blosum80.mat")


def run_pangtreebuild(output_dir: Path,
                      datatype: DataType,
                      multialignment: Union[Maf, Po],
                      fasta_provider: Union[FromFile, FromNCBI, ConstBaseProvider],
                      blosum: Blosum,
                      consensus_choice: str,
                      output_po: bool,
                      output_fasta: bool,
                      output_newick: bool,
                      missing_symbol: MissingBase,
                      metadata: Optional[MetadataCSV]=None,
                      hbmin: Optional[Hbmin] = None,
                      stop: Optional[Stop] = None,
                      p: Optional[P] = None,
                      fasta_path: Optional[Path] = None,
                      include_nodes: Optional[bool] = None
                      ) -> PangenomeJSON:
    start = time.time()
    logprocess.add_file_handler_to_logger(output_dir, "details", "details.log", propagate=False)
    logprocess.add_file_handler_to_logger(output_dir, "", "details.log", propagate=False)
    logprocess.remove_console_handler_from_root_logger()
    poagraph, dagmaf = None, None
    if isinstance(multialignment, Maf):
        poagraph, dagmaf = builder.build_from_dagmaf(multialignment, fasta_provider, metadata)
    elif isinstance(multialignment, Po):
        poagraph = builder.build_from_po(multialignment, metadata)

    consensus_output_dir = tools.get_child_dir(output_dir, "consensus")
    consensus_tree = None
    if consensus_choice == 'poa':
        consensus_tree = build_poa_affinity_tree(poagraph,
                                                 blosum,
                                                 consensus_output_dir,
                                                 hbmin,
                                                 True)
    elif consensus_choice == 'tree':
        consensus_tree = build_affinity_tree(poagraph,
                                             blosum,
                                             consensus_output_dir,
                                             stop,
                                             p,
                                             True)

    if output_po:
        pangenome_po = poagraph_to_PangenomePO(poagraph)
        tools.save_to_file(pangenome_po, tools.get_child_path(output_dir, "poagraph.po"))

    if output_fasta:
        sequences_fasta = poagraph_to_fasta(poagraph)
        tools.save_to_file(sequences_fasta, tools.get_child_path(output_dir, "sequences.fasta"))
        if consensus_tree:
            consensuses_fasta = affinity_tree_to_fasta(poagraph, consensus_tree)
            tools.save_to_file(consensuses_fasta, tools.get_child_path(output_dir, "consensuses.fasta"))

    if output_newick:
        if metadata is not None:
            seq_id_to_metadata = {seq_id: seq.seqmetadata
                                  for seq_id, seq in poagraph.sequences.items()}
        else:
            seq_id_to_metadata = None

        affinity_tree_newick = consensus_tree.as_newick(seq_id_to_metadata,
                                                        separate_leaves=True)

        tools.save_to_file(affinity_tree_newick, tools.get_child_path(output_dir, "affinity_tree.newick"))

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
                                     output_with_nodes=include_nodes,
                                     verbose=True,
                                     raw_maf=False,
                                     fasta_provider=str(type(fasta_provider).__name__),
                                     missing_base_symbol=missing_symbol.value,
                                     fasta_source_file=fasta_path,
                                     consensus_type=consensus_choice,
                                     hbmin=hbmin.value if hbmin else None,
                                     stop=stop.value if stop else None,
                                     p=p.value if p else None)

    pangenomejson = to_PangenomeJSON(task_parameters=task_parameters,
                                     poagraph=poagraph,
                                     dagmaf=dagmaf,
                                     affinity_tree=consensus_tree)
    pangenome_json_str = to_json(pangenomejson)
    tools.save_to_file(pangenome_json_str, tools.get_child_path(output_dir, "pangenome.json"))
    return pangenomejson


