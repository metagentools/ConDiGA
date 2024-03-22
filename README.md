<p align="center">
  <img src="https://raw.githubusercontent.com/metagentools/ConDiGA/develop/condiga_logo.png" width="200" title="condiga logo" alt="condiga logo">
</p>

# ConDiGA: Contigs Directed Gene Annotation

[![DOI](https://img.shields.io/badge/DOI-10.1186/s40168--024--01775--3-blue)](https://doi.org/10.1186/s40168-024-01775-3)
![GitHub](https://img.shields.io/github/license/metagentools/ConDiGA)
[![Anaconda-Server Badge](https://anaconda.org/bioconda/condiga/badges/version.svg)](https://anaconda.org/bioconda/condiga)
[![Bioconda Downloads](https://img.shields.io/conda/dn/bioconda/condiga)](https://img.shields.io/conda/dn/bioconda/condiga)
[![PyPI version](https://badge.fury.io/py/condiga.svg)](https://badge.fury.io/py/condiga)
[![Downloads](https://static.pepy.tech/badge/condiga)](https://pepy.tech/project/condiga)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/metagentools/ConDiGA/develop)
[![CI](https://github.com/metagentools/ConDiGA/actions/workflows/testing.yml/badge.svg)](https://github.com/metagentools/ConDiGA/actions/workflows/testing.yml)


**ConDiGA** (**Con**tigs **Di**rected **G**ene **A**nnotation) is an accurate taxonomic annotation pipeline from metagenomic data to construct accurate protein sequence databases for deep metaproteomic coverage. 

## Setting up ConDiGA

### Option 1: Installing ConDiGA using conda (recommended)

You can install ConDiGA from bioconda at [https://anaconda.org/bioconda/condiga](https://anaconda.org/bioconda/condiga). Make sure you have [`conda`](https://docs.conda.io/en/latest/) installed.

```bash
# create conda environment and install condiga
conda create -n condiga -c conda-forge -c bioconda condiga

# activate environment
conda activate condiga
```

### Option 2: Installing ConDiGA using pip

You can install ConDiGA from PyPI at [https://pypi.org/project/condiga/](https://pypi.org/project/condiga/). Make sure you have [`pip`](https://pip.pypa.io/en/stable/) installed.

```bash
pip install condiga
```

**Note**: If you use pip to setup ConDiGA, you will have to install [Minimap2](https://github.com/lh3/minimap2#install) and [TaxonKit](https://github.com/shenwei356/taxonkit) manually and add it to your system path. Irrespective of the package manager, if you want to use Kaiju results, you have to [download and setup the NCBI taxdump database for TaxonKit](https://bioinf.shenwei.me/taxonkit/download/).

### Test the setup

After setting up, run the following command to ensure that `condiga` is working.

```
condiga --help
```

### Usage

```
Usage: condiga [OPTIONS]

  ConDiGA: Contigs directed gene annotation for accurate protein sequence
  database construction in metaproteomics.

Options:
  -c, --contigs PATH              path to the contigs file  [required]
  -ta, --taxa PATH                path to the taxanomic classification results
                                  file  [required]
  -g, --genes PATH                path to the genes file  [required]
  -cov, --coverages PATH          path to the contig coverages file
                                  [required]
  -as, --assembly-summary PATH    path to the assembly_summary.txt file
                                  [required]
  -ra, --rel-abundance FLOAT RANGE
                                  minimum relative abundance cut-off
                                  [default: 0.0001; 0<=x<=1]
  -gc, --genome-coverage FLOAT RANGE
                                  minimum genome coverage cut-off  [default:
                                  0.001; 0<=x<=1]
  -mt, --map-threshold FLOAT RANGE
                                  minimum mapping length threshold cut-off
                                  [default: 0.5; 0<=x<=1]
  -t, --nthreads INTEGER          number of threads to use  [default: 8]
  -o, --output PATH               path to the output folder  [required]
  --help                          Show this message and exit.
```

## Preprocessing

Before running ConDiGA, you have to process your data as follows.

### Step 1: Assemble reads into contigs

You have to assemble your reads into contigs using [MEGAHIT](https://github.com/voutcn/megahit) as follows. Currently, ConDiGA only supports MEGAHIT assemblies.

```
megahit -1 Reads/reads_1.fq.gz -2 Reads/reads_2.fq.gz -o MEGAHIT_output -t 16
```

### Step 2: Taxonomically annotate contigs

Next, you have to perform taxonomic annotation on your contigs. You can use any tool such as [Kraken2](https://ccb.jhu.edu/software/kraken2/), [Kaiju](https://bioinformatics-centre.github.io/kaiju/) or even [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi).

As an example, let's run [Kraken2](https://ccb.jhu.edu/software/kraken2/) as follows. `$DBNAME` is the path to your Kraken database.

```
kraken2 --threads 16 --db $DBNAME --use-names --output kraken_res_0.1.txt --confidence 0.1 --report kraken_report_0.1.txt MEGAHIT_output/final.contigs.fa
```

Now, you can run the `convert` command to convert your result to a form that can be used as input to `condiga`. The result will be saved to the `Kraken` folder. Currently, `convert` supports results from Kraken2, Kaiju and BLAST.

```
mkdir Kraken
convert -i kraken_res_0.1.txt -t kraken -o Kraken
```

**NOTE:** Since, different annotation tools output results in different formats, you have to format the annotation results using `covert` which will output the result in a standard format readable by ConDiGA.

### Step 3: Obtain coverage of contigs

You can use [CoverM](https://github.com/wwood/CoverM) to get the coverage values of contigs as follows.

```
coverm contig -1 Reads/reads_1.fastq -2 Reads/reads_2.fastq -r MEGAHIT_output/final.contigs.fa -o contig_coverage.tsv -t 16
```

### Step 4: Predict genes in contigs

You can predict the genes in the contigs using [MetaGeneMark](http://exon.gatech.edu/meta_gmhmmp.cgi) as follows. You will find the nucleotide and amino acid sequences of the predicted genes in a file named `final.contigs.fa.lst`.

```
gmhmmp -m MetaGeneMark_v1.mod final.contigs.fa
```

### Step 5: Download `assembly_summary.txt` file.

You can download the assembly summary file for bacteria from [NCBI](https://www.ncbi.nlm.nih.gov/genome/doc/ftpfaq/) as follows.

```
wget https://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt
```

## Running ConDiGA

Once you have preprocessed your data and obtained all the necessary files, you can run `condiga` as follows.

```
condiga -c final.contigs.fa -ta Kraken/kraken_result.txt -g final.contigs.fa.lst -cov contig_coverages.tsv -as assembly_summary.txt -o <output_folder>
```

## Output

The output of ConDiGA will contain the following main files and folders.

* `genes.species.mapped.xlsx` contains the gene annotation results
* `all_genes.fna` contains nucleotide sequences of the predicted genes
* `all_genes.faa` contains amino acid sequences of the predicted genes
* `all_genes.output` contains `minimap2` mapping results for the predicted genes
* `Assemblies` contains FASTA files of the downloaded reference genomes

##  Issues and Questions

If you have any questions, issues or suggestions, please post them under [ConDiGA Issues](https://github.com/metagentools/ConDiGA/issues).

## Contributing to ConDiGA

Are you interested in contributing to the ConDiGA project? If so, you can check out the contributing guidelines in [CONTRIBUTING.md](https://github.com/metagentools/ConDiGA/blob/develop/CONTRIBUTING.md).


## Acknowledgement

The ConDiGA logo was generated using [DALL·E 3](https://openai.com/dall-e-3) from [OpenAI](https://openai.com/) with the following prompt.
> Create an icon that visually represents the concept of contigs directed gene annotation for a tool logo ensuring the background is completely transparent.

## Citation

ConDiGA is published in [Microbiome](https://microbiomejournal.biomedcentral.com/articles/10.1186/s40168-024-01775-3) at DOI: [10.1186/s40168-024-01775-3](https://doi.org/10.1186/s40168-024-01775-3).

If you use ConDiGA in your work, please as
> Wu, E., Mallawaarachchi, V., Zhao, J. et al. Contigs directed gene annotation (ConDiGA) for accurate protein sequence database construction in metaproteomics. Microbiome 12, 58 (2024). https://doi.org/10.1186/s40168-024-01775-3

```bibtex
@article{Wu2024,
author={Wu, Enhui and Mallawaarachchi, Vijini and Zhao, Jinzhi and Yang, Yi and Liu, Hebin and Wang, Xiaoqing and Shen, Chengpin and Lin, Yu and Qiao, Liang},
title={Contigs directed gene annotation (ConDiGA) for accurate protein sequence database construction in metaproteomics},
journal={Microbiome},
year={2024},
month={Mar},
day={19},
volume={12},
number={1},
pages={58},
abstract={Microbiota are closely associated with human health and disease. Metaproteomics can provide a direct means to identify microbial proteins in microbiota for compositional and functional characterization. However, in-depth and accurate metaproteomics is still limited due to the extreme complexity and high diversity of microbiota samples. It is generally recommended to use metagenomic data from the same samples to construct the protein sequence database for metaproteomic data analysis. Although different metagenomics-based database construction strategies have been developed, an optimization of gene taxonomic annotation has not been reported, which, however, is extremely important for accurate metaproteomic analysis.},
issn={2049-2618},
doi={10.1186/s40168-024-01775-3},
url={https://doi.org/10.1186/s40168-024-01775-3}
}
```
**NOTE:** The database created by ConDiGA is described as MD3 in the manuscript.

Also, please cite the following tools used by ConDiGA, the assembler and the relevant taxonomic annotation tool used to obtain the results.

* Zhu W, Lomsadze A, Borodovsky M. Ab initio gene identification in metagenomic sequences. Nucleic acids research, 38 (12): 132-132 (2010). [https://doi.org/10.1093/nar/gkq275](https://doi.org/10.1093/nar/gkq275)
* Li H. Minimap2: pairwise alignment for nucleotide sequences. Bioinformatics, 34:3094-3100 (2018). [https://doi.org/10.1093/bioinformatics/bty191](https://doi.org/10.1093/bioinformatics/bty191)
* Woodcroft BJ, Newell R, CoverM: Read coverage calculator for metagenomics (2017). [https://github.com/wwood/CoverM](https://github.com/wwood/CoverM)
