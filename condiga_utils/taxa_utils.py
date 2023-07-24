def get_taxa_result(taxa, contig_lengths):
    taxid_total_len = {}

    species_names_taxid = {}

    taxid_list = []

    contig_taxid = {}

    taxid_contigs = {}

    taxid_to_species = {}

    species_names_taxid_length = {}

    with open(taxa, "r") as myfile:
        for line in myfile.readlines():
            strings = line.strip().split("\t")

            species_strings = strings[2].split(" ")

            if (
                len(species_strings) > 1
                and "unclassified" not in strings[2]
                and "complex" not in strings[2]
                and " group " not in strings[2]
                and "Human" not in strings[2]
                and "phage" not in strings[2]
                and "cellular organisms" not in strings[2]
            ):
                taxid = strings[1]

                my_species = ""

                if species_strings[0] == "Candidatus" or species_strings[0] == "MAG:":
                    if len(species_strings) > 2:
                        my_species = (
                            species_strings[0]
                            + " "
                            + species_strings[1]
                            + " "
                            + species_strings[2]
                        )
                    else:
                        my_species = species_strings[0] + " " + species_strings[1]
                elif species_strings[1] != "sp.":
                    my_species = species_strings[0] + " " + species_strings[1]
                # else:
                #     my_species = strings[2]

                if my_species != "":
                    taxid_to_species[taxid] = my_species
                    contig_taxid[strings[0]] = taxid

                    if taxid not in taxid_list:
                        taxid_list.append(taxid)

                    if my_species in species_names_taxid:
                        species_names_taxid[my_species].add(taxid)
                    else:
                        species_names_taxid[my_species] = set([taxid])

                    if taxid not in taxid_contigs:
                        taxid_contigs[taxid] = [strings[0]]
                    else:
                        taxid_contigs[taxid].append(strings[0])

                    if taxid not in taxid_total_len:
                        taxid_total_len[taxid] = contig_lengths[strings[0]]
                    else:
                        taxid_total_len[taxid] += contig_lengths[strings[0]]

                    if my_species not in species_names_taxid_length:
                        species_names_taxid_length[my_species] = {}
                        species_names_taxid_length[my_species][taxid] = contig_lengths[
                            strings[0]
                        ]
                    else:
                        if taxid not in species_names_taxid_length[my_species]:
                            species_names_taxid_length[my_species][
                                taxid
                            ] = contig_lengths[strings[0]]
                        else:
                            species_names_taxid_length[my_species][
                                taxid
                            ] += contig_lengths[strings[0]]

    for species in species_names_taxid_length:
        sorted_taxids = {
            k: v
            for k, v in sorted(
                species_names_taxid_length[species].items(),
                reverse=True,
                key=lambda item: item[1],
            )
        }
        species_names_taxid_length[species] = sorted_taxids

    return (
        taxid_total_len,
        species_names_taxid,
        taxid_list,
        contig_taxid,
        taxid_contigs,
        taxid_to_species,
        species_names_taxid_length,
    )
