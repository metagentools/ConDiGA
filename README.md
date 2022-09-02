# ConDiGA
**Con**tigs **Di**rected **G**ene **A**nnotation for accurate protein sequence database construction in metaproteomics

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

Once you have installed `conda`, make sure you are in the `ConDiGA` folder. Now run the following commands to create a `conda` environment and activate it to run `phables`.

```
conda env create -f environment.yml
conda activate condiga
```

### Using `pip`
You can run the following command to install phables using `pip`. Make sure you are in the `ConDiGA` folder.

```
pip install .
```

**Note**: If you use pip to setup ConDiGA, you will have to install [Minimap2](https://github.com/lh3/minimap2#install) manually and add it to your system path.

### Test the setup

After setting up, run the following command to ensure that `condiga` is working.

```
condiga --help
```

## Usage

```
Usage: condiga [OPTIONS]

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
