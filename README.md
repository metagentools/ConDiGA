# ConDiGA

[![DOI](https://img.shields.io/badge/Preprint_DOI-10.1101/2023.04.19.537311-blue)](https://doi.org/10.1101/2023.04.19.537311)
[![Anaconda-Server Badge](https://anaconda.org/bioconda/condiga/badges/version.svg)](https://anaconda.org/bioconda/condiga)
[![PyPI version](https://badge.fury.io/py/condiga.svg)](https://badge.fury.io/py/condiga)

[![CI](https://github.com/metagentools/ConDiGA/actions/workflows/testing.yml/badge.svg)](https://github.com/metagentools/ConDiGA/actions/workflows/testing.yml)
![GitHub](https://img.shields.io/github/license/metagentools/ConDiGA)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/metagentools/ConDiGA/develop)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


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

## Citation

If you use ConDiGA in your work, please cite the [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2023.04.19.537311v1) as follows.

```bibtex
@article {Wu2023.04.19.537311,
	author = {Enhui Wu and Vijini Mallawaarachchi and Jinzhi Zhao and Yi Yang and Hebin Liu and Xiaoqing Wang and Chengpin Shen and Yu Lin and Liang Qiao},
	title = {Contigs directed gene annotation (ConDiGA) for accurate protein sequence database construction in metaproteomics},
	elocation-id = {2023.04.19.537311},
	year = {2023},
	doi = {10.1101/2023.04.19.537311},
	publisher = {Cold Spring Harbor Laboratory},
	abstract = {Microbiota are closely associated to human health and disease. Metaproteomics can provide a direct means to identify microbial proteins in microbiota for compositional and functional characterization. However, in-depth and accurate metaproteomics is still limited due to the extreme complexity and high diversity of microbiota samples. One of the main challenges is constructing a protein sequence database that best fits the microbiota sample. Herein, we proposed an accurate taxonomic annotation pipeline from metagenomic data for deep metaproteomic coverage, namely contigs directed gene annotation (ConDiGA). We mixed 12 known bacterial species to derive a synthetic microbial community to benchmark metagenomic and metaproteomic pipelines. With the optimized taxonomic annotation strategy by ConDiGA, we built a protein sequence database from the metagenomic data for metaproteomic analysis and identified about 12,000 protein groups, which was very close to the result obtained with the reference proteome protein sequence database of the 12 species. We also demonstrated the practicability of the method in real fecal samples, achieved deep proteome coverage of human gut microbiome, and compared the function and taxonomy of gut microbiota at metagenomic level and metaproteomic level. Our study can tackle the current taxonomic annotation reliability problem in metagenomics-derived protein sequence database for metaproteomics. The unique dataset of metagenomic and the metaproteomic data of the 12 bacterial species is publicly available as a standard benchmarking sample for evaluating various analysis pipelines. The code of ConDiGA is open access at GitHub for the analysis of real microbiota samples.Competing Interest StatementThe authors have declared no competing interest.},
	URL = {https://www.biorxiv.org/content/early/2023/04/20/2023.04.19.537311},
	eprint = {https://www.biorxiv.org/content/early/2023/04/20/2023.04.19.537311.full.pdf},
	journal = {bioRxiv}
}

```
