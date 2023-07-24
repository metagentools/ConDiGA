def get_species_stats(
    species_names_taxid_length,
    taxid_file_len,
    taxid_contigs,
    contig_lengths,
    contig_coverages,
):
    # Length
    species_ref_length = {}
    species_contig_length = {}

    for species in species_names_taxid_length:
        species_ref_length[species] = 0
        species_contig_length[species] = 0

    # Coverage
    species_coverages = {}

    for species in species_names_taxid_length:
        species_coverages[species] = 0

    # Genome coverage
    species_genome_coverages = {}

    for species in species_names_taxid_length:
        species_genome_coverages[species] = 0

    # Relative abundance
    species_rel_abundance = {}

    for species in species_names_taxid_length:
        species_rel_abundance[species] = 0

    total_reads_mapped = 0

    for species in species_names_taxid_length:
        # Length

        total_sum = 0
        total_contig_length_sum = 0
        species_count = 0

        for taxid in species_names_taxid_length[species]:
            if taxid in taxid_file_len:
                if taxid_file_len[taxid] != 0:
                    total_sum += taxid_file_len[taxid]
                    total_contig_length_sum += species_names_taxid_length[species][
                        taxid
                    ]
                    species_count += 1

        species_contig_length[species] = total_contig_length_sum

        if species_count != 0:
            species_ref_length[species] = total_sum / species_count
        else:
            species_ref_length[species] = 0

        # Coverage

        total_sum = 0
        total_contig_length = 0

        for taxid in species_names_taxid_length[species]:
            for contig in taxid_contigs[taxid]:
                total_sum += contig_lengths[contig] * contig_coverages[contig]
                total_contig_length += contig_lengths[contig]

        if total_contig_length != 0:
            species_coverages[species] = total_sum / total_contig_length
        else:
            species_coverages[species] = 0

        # Genome coverage

        total_contig_length = 0

        for taxid in species_names_taxid_length[species]:
            for contig in taxid_contigs[taxid]:
                total_contig_length += contig_lengths[contig]

        if total_contig_length != 0 and species_ref_length[species] != 0:
            species_genome_coverages[species] = (
                total_contig_length / species_ref_length[species]
            )
        else:
            species_genome_coverages[species] = 0

        # Relative abundance

        species_reads = 0

        for taxid in species_names_taxid_length[species]:
            for contig in taxid_contigs[taxid]:
                species_reads += contig_lengths[contig] * contig_coverages[contig]
                total_reads_mapped += contig_lengths[contig] * contig_coverages[contig]

        species_rel_abundance[species] = species_reads

    for species in species_names_taxid_length:
        species_rel_abundance[species] = (
            species_rel_abundance[species] / total_reads_mapped
        )

    sorted_species = {
        k: v
        for k, v in sorted(
            species_rel_abundance.items(), reverse=True, key=lambda item: item[1]
        )
    }
    species_rel_abundance = sorted_species

    return species_genome_coverages, species_rel_abundance
