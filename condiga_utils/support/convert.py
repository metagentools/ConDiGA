#!/usr/bin/env python3

import subprocess
import sys

import click

__author__ = "Vijini Mallawaarachchi and Yu Lin"
__copyright__ = "Copyright 2022, ConDiGA Project"
__license__ = "MIT"
__version__ = "0.2.2"
__maintainer__ = "Vijini Mallawaarachchi"
__email__ = "viji.mallawaarachchi@gmail.com"
__status__ = "Development"


# Setup arguments
# ----------------------------------------------------------------------


@click.command()
@click.option(
    "--input",
    "-i",
    required=True,
    help="path to the taxanomic classification results file",
    type=click.Path(exists=True),
)
@click.option(
    "--tool",
    "-t",
    required=True,
    help="taxonomic classification tool used (Supports Kraken, Kaiju and BLAST)",
    type=click.Choice(["kraken", "kaiju", "blast"], case_sensitive=False),
)
@click.option(
    "--nthreads",
    help="number of threads to use",
    type=int,
    default=8,
    show_default=True,
    required=False,
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="path to the output folder",
    type=click.Path(exists=True),
)
def main(input, tool, nthreads, output):
    """
    convert: Convert taxonomic classification results to a format that can supplied as input to ConDiGA
    """

    if tool.lower() == "kraken":
        kraken_species = {}
        kraken_taxid = {}

        with open(input, "r") as myfile:
            for line in myfile.readlines():
                if line.strip().startswith("C"):
                    strings = line.strip().split("\t")
                    tax_data = strings[2].split(" (")
                    kraken_species[strings[1]] = tax_data[0]
                    kraken_taxid[strings[1]] = tax_data[1][6:-1]

        with open(output + "/kraken_result.txt", "w") as myfile:
            for contig in kraken_species:
                myfile.write(
                    f"{contig}\t{kraken_taxid[contig]}\t{kraken_species[contig]}\n"
                )

    elif tool.lower() == "kaiju":

        # Check if taxonkit is installed
        try:
            p = subprocess.run(["which", "taxonkit"], capture_output=True)
            if p.returncode != 0:
                raise Exception("Command does not exist")
        except:
            print("taxonkit does not exist. Please install from https://github.com/shenwei356/taxonkit")
            sys.exit(1)

        kaiju_taxid = {}
        kaiju_species = {}

        taxid_species = {}

        with open(output + "/kaiju_result.txt", "w") as myfile1:
            with open(input, "r") as myfile:
                for line in myfile.readlines():
                    if line.strip().startswith("C"):
                        strings = line.strip().split("\t")
                        taxid = strings[2]
                        is_found = False

                        if taxid not in taxid_species:
                            result = subprocess.run(
                                [
                                    "taxonkit",
                                    "list",
                                    "--ids",
                                    taxid,
                                    "-n",
                                    "--threads",
                                    str(nthreads),
                                ],
                                capture_output=True,
                                text=True,
                            )
                            names = result.stdout
                            name_parts = names.strip().split("\n")[0].split()
                            if len(name_parts) > 2:
                                sci_name = " ".join(name_parts[1:])
                                print(strings[1], taxid, sci_name)
                                kaiju_taxid[strings[1]] = taxid
                                kaiju_species[strings[1]] = sci_name
                                taxid_species[taxid] = sci_name
                                is_found = True
                        else:
                            is_found = True
                            print(strings[1], taxid, taxid_species[taxid])
                            kaiju_taxid[strings[1]] = taxid
                            kaiju_species[strings[1]] = taxid_species[taxid]

                        if is_found:
                            myfile1.write(
                                f"{strings[1]}\t{kaiju_taxid[strings[1]]}\t{kaiju_species[strings[1]]}\n"
                            )

    elif tool.lower() == "blast":
        blast_species = {}
        blast_taxid = {}
        blast_accession = {}

        with open(input, "r") as myfile:
            for line in myfile.readlines():
                strings = line.strip().split("\t")

                if float(strings[10]) < 1e-10:
                    blast_species[strings[0]] = strings[17]
                    blast_accession[strings[0]] = strings[1].split("|")[3]
                    blast_taxid[strings[0]] = strings[2]

        with open(output + "/blast_result.txt", "w") as myfile:
            for genome in blast_species:
                myfile.write(
                    f"{genome}\t{blast_taxid[genome]}\t{blast_species[genome]}\t{blast_accession[genome]}\n"
                )
