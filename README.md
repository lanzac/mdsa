# MDVerse simulations analysis

## Setup your environment

Clone the repository (temp link):

```bash
git clone https://github.com/lanzac/mdsa.git
```

Move to the new directory:

```bash
cd mdsa
```

Install [miniconda](https://docs.conda.io/en/latest/miniconda.html).

Install [mamba](https://github.com/mamba-org/mamba):

```bash
conda install mamba -n base -c conda-forge
```

Create the `mdsa` conda environment:
```
mamba env create -f binder/environment.yml
```
-> Mamba ne marche pas ! 
utiliser : 
```
conda env create -f binder/environment.yml
```

Load the `mdsa` conda environment:
```
conda activate mdsa
```

Note: you can also update the conda environment with:

```bash
mamba env update -f binder/environment.yml
```

To deactivate an active environment, use

```
conda deactivate
```

## Get data

Data files are directly downloaded from [Zenodo](https://doi.org/10.5281/zenodo.7856523).


## Run the web application

```bash
streamlit run MDverse_simulation_analysis.py
```