import collections
import csv
import re
import subprocess
from collections import defaultdict

import xlsxwriter


def write_nt_gene_seqs(genes, output):
    gene_nt_seq = {}

    for seq in get_seqs(genes):
        if "_nt|" in seq:
            strings = seq.split("|")

            gene_id = strings[0][1:]

            gene_nt_seq[gene_id] = seq

    with open(f"{output}/all_genes.fna", "w") as ntfile:
        for gene in gene_nt_seq:
            ntfile.write(gene_nt_seq[gene])


def get_seqs(path):
    active = ""

    for line in open(path):
        if line[0] == ">":
            active += line
        elif len(active) > 0 and len(line.strip()) != 0:
            active += line
        elif len(line.strip()) == 0 and len(active) > 0:
            yield active
            active = ""
    if len(active) > 0:
        yield active


def align_genes_to_refs(threshold, nthreads, output):
    # Concatenate all references
    command = f"cat {output}/Reference_Sequences/*.fna > {output}/Reference_Sequences/refs.fna"
    subprocess.run(command, shell=True)

    # Run minimap2
    command = f"minimap2 -t {nthreads} {output}/Reference_Sequences/refs.fna {output}/all_genes.fna > {output}/all_genes.paf"
    subprocess.run(command, shell=True)

    # Remove concatenated reference files
    command = f"rm {output}/Reference_Sequences/refs.fna"
    subprocess.run(command, shell=True)

    contig_ref = defaultdict(list)
    contig_ref_aln_length = defaultdict(list)
    contig_length = {}

    for line in open(f"{output}/all_genes.paf"):
        data = line.strip().split("\t")
        #     1	string	Query sequence name
        #     2	int	Query sequence length
        #     3	int	Query start (0-based; BED-like; closed)
        #     4	int	Query end (0-based; BED-like; open)
        #     5	char	Relative strand: "+" or "-"
        #     6	string	Target sequence name
        #     7	int	Target sequence length
        #     8	int	Target start on original strand (0-based)
        #     9	int	Target end on original strand (0-based)
        #     10	int	Number of residue matches
        #     11	int	Alignment block length
        #     12	int	Mapping quality (0-255; 255 for missing)

        qname = data[0]
        qlen = int(data[1])
        qstart = int(data[2])
        qqend = int(data[3])
        char = data[4]
        tname = data[5]
        tlen = int(data[6])
        tstart = int(data[7])
        aln_len = int(data[10])
        flag = int(data[11])

        if not flag == 255:
            contig_ref[qname].append(tname)
            contig_ref_aln_length[qname].append(aln_len)
            contig_length[qname] = qlen

    with open(f"{output}/all_genes.output", "w+") as f:
        for k, v in contig_ref.items():
            best = None
            best_len = 0
            c_len = contig_length[k]

            if len(v) > 1:
                align_sum = 0

                for ref, l in zip(contig_ref[k], contig_ref_aln_length[k]):
                    align_sum += l

                if align_sum >= threshold * c_len and best_len < align_sum:
                    best_len = align_sum
                    best = ref

            elif contig_ref_aln_length[k][0] >= threshold * c_len:
                best = contig_ref[k][0]
                best_len = contig_ref_aln_length[k][0]
            else:
                best = "POOR MAPPING"
            f.write(f"{k}\t{best}\t{best_len}\n")


def get_genes_mapped_to_species(ref_ids, output):
    gene_bins = {}

    with open(f"{output}/all_genes.output", mode="r") as myfile:
        for line in myfile.readlines():
            strings = line.strip().split("\t")

            gene_num = strings[0].split("|")[0]

            for ref in ref_ids:
                if strings[1] in ref_ids[ref]:
                    if gene_num not in gene_bins:
                        gene_bins[gene_num] = ref
                    break

    return gene_bins


def get_aa_gene_seqs(
    genes, gene_bins, taxid_present, taxid_to_species, contig_taxid, k_val
):
    gene_seq = {}

    genes_contigs = {}

    gene_species_mapped = {}

    unmapped_count = 0

    for seq in get_seqs(genes):
        if "_aa|" in seq:
            strings = seq.split("|")

            gene_id = strings[0][1:]

            start_n = f"k{k_val}_"
            end_n = ""

            contig_id = seq.split(">")[-1].split(" ")[0]

            contig_num = int(
                re.search("%s(.*)%s" % (start_n, end_n), contig_id).group(1)
            )

            strings = seq.split(">")

            gene_id = strings[1].strip().split("|")[0]

            gene_seq[gene_id] = seq

            genes_contigs[gene_id] = contig_num

            has_bin = False

            if gene_id in gene_bins:
                if taxid_present[gene_bins[gene_id]]:
                    gene_species_mapped[gene_id] = taxid_to_species[gene_bins[gene_id]]

                    has_bin = True

                else:
                    if contig_id in contig_taxid:
                        gene_species_mapped[gene_id] = taxid_to_species[
                            contig_taxid[contig_id]
                        ]
                        has_bin = True

            if not has_bin:
                gene_species_mapped[gene_id] = "unmapped"
                unmapped_count += 1

    return gene_seq, genes_contigs, gene_species_mapped, unmapped_count


def write_aa_gene_seqs(gene_species_mapped, gene_seq, output):
    gene_species = {"GeneID": "Annotation"}

    with open(f"{output}/all_genes.faa", "w") as aafile:
        for gene in gene_species_mapped:
            gene_id = gene

            if gene_species_mapped[gene] == "unmapped":
                gene_species[gene_id] = "-"
            else:
                gene_species[
                    gene_id
                ] = f"[{gene_species_mapped[gene].replace('_', ' ')}]"

            aafile.write(gene_seq[gene])

    od = collections.OrderedDict(sorted(gene_species.items()))

    # Create a workbook and add a worksheet
    workbook_name = f"{output}/genes.species.mapped.xlsx"
    workbook = xlsxwriter.Workbook(workbook_name)
    worksheet = workbook.add_worksheet()

    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0

    # Iterate over the data and write it out row by row.
    for gene, species in od.items():
        worksheet.write(row, col, gene)
        worksheet.write(row, col + 1, species)
        row += 1

    workbook.close()

    # Write to csv file
    with open(f"{output}/genes.species.mapped.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in gene_species.items():
            writer.writerow([key, value])

    return workbook_name
