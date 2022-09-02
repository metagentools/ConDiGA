# ConDiGA
**Con**tigs **Di**rected **G**ene **A**nnotation for accurate protein sequence database construction in metaproteomics

## Usage

```
Usage: condiga.py [OPTIONS]

  ConDiGA: Contigs directed gene annotation for accurate protein sequence
  database construction in metaproteomics.

Options:
  -c, --contigs PATH            path to the contigs file  [required]
  -k, --kraken PATH             path to the kraken results file  [required]
  -g, --genes PATH              path to the genes file  [required]
  -cov, --coverages PATH        path to the contig coverages file  [required]
  -as, --assembly-summary PATH  path to the assembly_summary.txt file
                                [required]

  -k, --k_val INTEGER           k value used to assemble the contigs
                                [required]

  -ra, --rel-abundance FLOAT    minimum relative abundance cut-off
  -gc, --genome-coverage FLOAT  minimum genome coverage cut-off
  -mt, --map-threshold FLOAT    minimum mapping length threshold cut-off
  -t, --nthreads INTEGER        number of threads to use
  -o, --output PATH             path to the output folder  [required]
  --help                        Show this message and exit.
```
