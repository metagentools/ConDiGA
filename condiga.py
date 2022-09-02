#!/usr/bin/env python3

import logging
import time

import click

from condiga_utils.contig_utils import get_contig_lengths
from condiga_utils.kraken_utils import get_kraken_result
from condiga_utils.genome_utils import download_genomes, rename_and_copy_genomes, get_ref_lengths, get_ref_ids
from condiga_utils.coverage_utils import get_coverage
from condiga_utils.species_utils import get_species_stats
from condiga_utils.gene_utils import write_nt_gene_seqs, write_aa_gene_seqs, align_genes_to_refs, get_genes_mapped_to_species, get_aa_gene_seqs

__author__ = "Vijini Mallawaarachchi and Yu Lin"
__copyright__ = "Copyright 2022, ConDiGA Project"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Vijini Mallawaarachchi"
__email__ = "vijini.mallawaarachchi@anu.edu.au"
__status__ = "Development"

# Sample command
# -------------------------------------------------------------------

# Setup arguments
# ----------------------------------------------------------------------


@click.command()
@click.option(
    "--contigs",
    "-c",
    required=True,
    help="path to the contigs file",
    type=click.Path(exists=True),
)
@click.option(
    "--kraken",
    "-k",
    required=True,
    help="path to the kraken results file",
    type=click.Path(exists=True),
)
@click.option(
    "--genes",
    "-g",
    required=True,
    help="path to the genes file",
    type=click.Path(exists=True),
)
@click.option(
    "--coverages",
    "-cov",
    required=True,
    help="path to the contig coverages file",
    type=click.Path(exists=True),
)
@click.option(
    "--assembly-summary",
    "-as",
    required=True,
    help="path to the assembly_summary.txt file",
    type=click.Path(exists=True),
)
@click.option(
    "--k_val",
    "-k",
    default=8,
    required=True,
    help="k value used to assemble the contigs",
    type=int,
)
@click.option(
    "--rel-abundance",
    "-ra",
    default=0.0001,
    required=False,
    help="minimum relative abundance cut-off",
    type=float,
)
@click.option(
    "--genome-coverage",
    "-gc",
    default=0.001,
    required=False,
    help="minimum genome coverage cut-off",
    type=float,
)
@click.option(
    "--map-threshold",
    "-mt",
    default=0.5,
    required=False,
    help="minimum mapping length threshold cut-off",
    type=float,
)
@click.option(
    "--nthreads",
    "-t",
    default=8,
    required=False,
    help="number of threads to use",
    type=int,
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="path to the output folder",
    type=click.Path(exists=True),
)
def main(contigs, kraken, genes, coverages, assembly_summary, k_val, rel_abundance, genome_coverage, map_threshold, nthreads, output):

    """ConDiGA: Contigs directed gene annotation for accurate protein sequence database construction in metaproteomics."""

    # Setup logger
    # ----------------------------------------------------------------------

    logger = logging.getLogger("condiga 0.1")
    logger.setLevel(logging.DEBUG)
    logging.captureWarnings(True)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    consoleHeader = logging.StreamHandler()
    consoleHeader.setFormatter(formatter)
    consoleHeader.setLevel(logging.INFO)
    logger.addHandler(consoleHeader)

    # Setup output path for log file
    fileHandler = logging.FileHandler(f"{output}/condiga.log")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    logger.info("Welcome to ConDiGA: Contigs directed gene annotation for accurate protein sequence database construction in metaproteomics.")

    logger.info(f"Input arguments: ")
    logger.info(f"Contigs file: {contigs}")
    logger.info(f"Kraken results file: {kraken}")
    logger.info(f"Genes file: {genes}")
    logger.info(f"Contig coverages file: {coverages}")
    logger.info(f"Path to assembly_summary.txt file: {assembly_summary}")
    logger.info(f"Minimum relative abundance cut-off: {rel_abundance}")
    logger.info(f"Minimum genome coverage cut-off: {genome_coverage}")
    logger.info(f"Minimum mapping length threshold cut-off: {map_threshold}")
    logger.info(f"Output folder: {output}")

    start_time = time.time()

    # Get contig lengths
    # ----------------------------------------------------------------------

    contig_lengths = get_contig_lengths(contigs)

    # Get kraken result
    # ----------------------------------------------------------------------

    taxid_total_len, species_names_taxid, taxid_list, contig_taxid, taxid_contigs, taxid_to_species, species_names_taxid_length = get_kraken_result(kraken, contig_lengths)

    # Download genomes of taxids
    # ----------------------------------------------------------------------
    
    taxid_dates, taxid_urls, taxid_file_path, taxid_assembly_level, taxid_present = download_genomes(taxid_list, assembly_summary, output)

    # Get length of references
    # ----------------------------------------------------------------------

    taxid_file_len = get_ref_lengths(taxid_present, taxid_file_path)

    # Get contig coverage values
    # ----------------------------------------------------------------------

    contig_coverages = get_coverage(coverages)
    
    # Get species genome coverage and relative abundance
    #

    species_genome_coverages, species_rel_abundance = get_species_stats(species_names_taxid_length, taxid_file_len, taxid_contigs, contig_lengths, contig_coverages)

    # Rename and copy selected species
    # ----------------------------------------------------------------------

    rename_and_copy_genomes(taxid_file_path, species_names_taxid_length, species_genome_coverages, species_rel_abundance, rel_abundance, genome_coverage, output)

    # Write nucleotide gene sequences
    # ----------------------------------------------------------------------

    write_nt_gene_seqs(genes, output)

    # Align genes to refs
    # ----------------------------------------------------------------------

    align_genes_to_refs(map_threshold, nthreads, output)

    # Get reference IDs
    # ----------------------------------------------------------------------

    ref_ids = get_ref_ids(output)

    # Get genes to mapped species
    # ----------------------------------------------------------------------

    gene_bins = get_genes_mapped_to_species(ref_ids, output)

    # Get aa gene seqs mapped
    # ----------------------------------------------------------------------

    gene_seq, genes_contigs, gene_species_mapped, unmapped_count = get_aa_gene_seqs(genes, gene_bins, taxid_present, taxid_to_species, contig_taxid, k_val)

    logger.info(f"Total number of genes: {len(gene_seq)}")
    logger.info(f"Number of genes mapped: {len(gene_seq)-unmapped_count}")
    logger.info(f"Percentage of genes mapped: {(len(gene_seq)-unmapped_count)/len(gene_seq)}")

    # Write amino acid gene sequences
    # ----------------------------------------------------------------------

    workbook_name = write_aa_gene_seqs(gene_species_mapped, gene_seq, output)

    logger.info(f"Gene annotation results can be found in {workbook_name}")

    # Get elapsed time
    # ----------------------------------------------------------------------

    # Determine elapsed time
    elapsed_time = time.time() - start_time

    # Print elapsed time for the process
    logger.info("Elapsed time: " + str(elapsed_time) + " seconds")

    # Exit program
    # ----------------------------------------------------------------------

    logger.info("Thank you for using condiga!")


if __name__ == "__main__":
    main()
