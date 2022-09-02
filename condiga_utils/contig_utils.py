import subprocess

from Bio import SeqIO

def get_contig_lengths(contigs):
    contig_lengths = {}

    for index, record in enumerate(SeqIO.parse(contigs, "fasta")):
        contig_lengths[record.id] = len(record.seq)

    return contig_lengths
