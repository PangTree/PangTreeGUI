import dash_html_components as html

def blank_link(string, href):
    return html.A(string, href=href, target="_blank")

"""-------------------------------LINKS--------------------------------------"""
# INDEX
build_logo_src = "https://image.flaticon.com/icons/svg/346/346195.svg"
vis_logo_src = "https://image.flaticon.com/icons/svg/346/346190.svg"
freepik_link = "https://www.flaticon.com/authors/freepik"
flaticon_link = "https://www.flaticon.com/"


# FORMATS
maf_info_link = "http://genome.ucsc.edu/FAQ/FAQformat.html#format5"
po_info_link = "https://github.com/PangTree/PangTreeBuild/blob/master/Documentation.md" \
               "#po-file-format-specification"
pograph_info_link = "https://doi.org/10.1093/bioinformatics/18.3.452"
mafgraph_info_link = "https://github.com/anialisiecka/Mafgraph"

# PACKAGE - PANGTREEBUILD
pangtreebuild_link = "https://github.com/PangTree/PangTreeBuild"
metadata_form_example_link = "https://github.com/PangTree/PangTreeBuild/blob/master/" \
                                    "example_data/Simulated/toy_example/metadata.csv"
maf_form_example_link = "https://github.com/PangTree/PangTreeBuild/blob/master/" \
                        "example_data/Simulated/toy_example/f.maf"

poa_alg_link = "https://doi.org/10.1093/bioinformatics/btg109"
tree_alg_link = "https://github.com/PangTree/PangTreeBuild#idea-and-algorithm-description"
b80_link = "https://github.com/PangTree/PangTreeGUI/blob/master/dash_app/dependencies/blosum80.mat"

ebola_data_link = "https://github.com/PangTree/PangTreeBuild/tree/master/example_data/Ebola"
toy_data_link = "https://github.com/PangTree/PangTreeBuild/tree/master/example_data/Simulated/toy_example"
"""-------------------------------INDEX--------------------------------------"""

"""------------------------------FORMATS-------------------------------------"""
maf_info = blank_link("MAF", href=maf_info_link)
po_info = blank_link("PO", href=po_info_link)
pograph_info = blank_link("Partial Order graph", href=pograph_info_link)
mafgraph_info = blank_link("Mafgraph", href=mafgraph_info_link)

metadata_example_info = blank_link("metadata.csv", href=metadata_form_example_link)
maf_example_link = blank_link("example.maf", href=maf_form_example_link)

"""------------------------------PACKAGE-------------------------------------"""
package_card_text = """
    #imports from pangtreebuild here...

    fasta_path = "example.fasta"

    fasta_provider = missings.FromFile(fasta_path)

    maf = msa.Maf(pathtools.get_file_content_stringio(maf_path), "example.maf")

    poagraph, dagmaf = builder.build_from_dagmaf(maf, fasta_provider)

    at = at_builders.build_affinity_tree(poagraph,\
                                         None,\
                                         current_output_dir,\
                                         at_params.Stop(0.99),\
                                         at_params.P(1),\
                                         True)\
    
    pangenomejson = json.to_PangenomeJSON(poagraph=poagraph,\
                                          affinity_tree=at)
    """

"""-------------------------- PANGTREEBUILD ---------------------------------"""
metadata_upload_form_text = """CSV with sequences metadata. It will be included in the 
    visualisation. The 'seqid' column is obligatory and must match sequences identifiers from 
    MULTIALIGNMENT file. Other columns are optional. Example file: """



