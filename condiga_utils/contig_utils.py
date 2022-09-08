import re

from Bio import SeqIO


def get_contig_lengths(contigs):
    contig_lengths = {}

    record_id = ""

    for index, record in enumerate(SeqIO.parse(contigs, "fasta")):
        contig_lengths[record.id] = len(record.seq)

        if record_id == "":
            record_id = record.id

    start_n = "k"
    end_n = "_"

    k_val = int(re.search(r"%s(.*)%s" % (start_n, end_n), record_id).group(1))

    return contig_lengths, k_val
