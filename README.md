# ConDiGA

![GitHub](https://img.shields.io/github/license/metagentools/ConDiGA)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**ConDiGA** (**Con**tigs **Di**rected **G**ene **A**nnotation) is an accurate taxonomic annotation pipeline from metagenomic data to construct accurate protein sequence databases for deep metaproteomic coverage. 

## Setting up ConDiGA

### Downloading ConDiGA

You can clone the ConDiGA repository to your machine.

```
git clone https://github.com/metagentools/ConDiGA.git
```

Now go into the `ConDiGA` folder using the command

```
cd ConDiGA/
```

### Using `conda`

Once you have installed `conda`, make sure you are in the `ConDiGA` folder. Now run the following commands to create a `conda` environment and activate it to run `condiga`.

```
conda env create -f environment.yml
conda activate condiga
```

### Using `pip`
You can run the following command to install `condiga` using `pip`. Make sure you are in the `ConDiGA` folder.

```
pip install .
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

You have to assemble your reads into contigs using [MEGAHIT](https://github.com/voutcn/megahit) as follows.

```
megahit -1 Reads/reads_1.fq.gz -2 Reads/reads_2.fq.gz --k-min 21 --k-max 141 -o MEGAHIT_output -t 16
```

### Step 2: Taxonomically annotate contigs

Next, you have to taxonomically annotate your contigs. You can use any tool such as [Kraken2](https://ccb.jhu.edu/software/kraken2/), [Kaiju](https://bioinformatics-centre.github.io/kaiju/) or even [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi).

As an example, let's run [Kraken2](https://ccb.jhu.edu/software/kraken2/) as follows. `$DBNAME` is the path to your Kraken database.

```
kraken2 --threads 16 --db $DBNAME --use-names --output kraken_res_0.1.txt --confidence 0.1 --report kraken_report_0.1.txt MEGAHIT_output/final.contigs.fa
```

Now, you can run the `convert` command to convert your result to a form that can be used as input to `condiga`.
```
mkdir Kraken
convert -i kraken_res_0.1.txt -t kraken -o Kraken
```

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

