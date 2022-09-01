#!/usr/bin/env python3

import collections
import csv
import glob
import gzip
import logging
import os
import re
import shutil
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timedelta

import click
import xlsxwriter
from Bio import SeqIO

__author__ = "Vijini Mallawaarachchi"
__copyright__ = "Copyright 2022, ConDiGA Project"
__license__ = "GPL-3.0"
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
    "--coverages",
    "-cov",
    required=True,
    help="path to the contig coverages file",
    type=click.Path(exists=True),
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="path to the output folder",
    type=click.Path(exists=True),
)
def main(contigs, kraken, coverages, output):

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

    logger.info(
        "Welcome to ConDiGA: Contigs directed gene annotation for accurate protein sequence database construction in metaproteomics."
    )

    logger.info(f"Input arguments: ")
    logger.info(f"Contigs file: {contigs}")
    logger.info(f"Kraken results file: {kraken}")
    logger.info(f"Contig coverages file: {coverages}")
    logger.info(f"Output folder: {output}")

    start_time = time.time()


if __name__ == "__main__":
    main()
