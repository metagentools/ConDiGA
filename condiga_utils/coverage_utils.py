def get_coverage(coverages):
    contig_coverages = {}

    with open(coverages, "r") as myfile:
        for line in myfile.readlines():
            if not line.startswith("Contig"):
                strings = line.strip().split()

                contig_coverages[strings[0]] = float(strings[1])

    return contig_coverages
