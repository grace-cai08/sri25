# GCM Clustering Script

This project provides a pipeline for running the General Clustering Method (GCM) on a given input file. The pipeline involves formatting the input, running clustering, and remapping the partition results. The core functionality is written in Python, while the clustering algorithm itself is compiled into an executable binary (`a.out`).

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Compilation of GCM Code](#compilation-of-gcm-code)
- [Usage](#usage)
- [Arguments](#arguments)
- [Example](#example)
- [Directory Structure](#directory-structure)

## Requirements

Before running the scripts, ensure you have the following installed:

- **Python 3.7 or higher**
- **Bash shell**
- **GCC** (for compiling the GCM code)
- `a.out` binary (generated from GCM source code as explained below)

## Setup

1. Clone this repository or download the scripts to a working directory:
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2. Install any required Python packages. This script relies only on Python's standard library, so no external libraries are needed.

## Compilation of GCM Code

Before running the clustering process, you need to compile the GCM code to generate the `a.out` binary.

### Steps to Compile:

1. Clone the code as per the details in the [GCM repository](https://github.com/prameshsingh/generalized-modularity-density)
2. Use `gcc` to compile the GCM code:
    ```bash
    gcc main.c help.c rg.c -fopenmp -lm
    ```

3. Copy the `a.out` binary in the working directory where the Python scripts are located.

### Note:

- The `a.out` binary is used by the script during the clustering process, so ensure it is correctly compiled and accessible in the same folder.

## Usage

To run the GCM clustering pipeline, use the following command:

```bash
python gcm_script.py <input_file> [--output_dir <output_directory>] [--output_file <output_file_name>] [--seed <random_seed>] [--chi <chi_value>] [--sep <separator>]
```

### Example:

```bash
python gcm_script.py input.txt --output_dir ./results --output_file clustering_result.txt --seed 98765 --chi 0.05 --sep comma
```

This command will:

- Take `input.txt` as the input file.
- Format and process the file using the `format_edgelist.py` script.
- Run the GCM algorithm using the compiled `a.out` binary.
- Save the output in the `./results` directory as `clustering_result.txt`.

## Arguments

- `input_file` (required): The input file for clustering.
- `--output_dir` (optional): Directory where the output will be saved. Defaults to the current working directory.
- `--output_file` (optional): Name of the output file. Defaults to `clustering_output.txt`.
- `--seed` (optional): Seed for random number generation. Default is `12345`.
- `--chi` (optional): Chi value for the clustering algorithm. Default is `0.0`.
- `--sep` (optional): Separator to use when formatting the input file. Options: `"space"`, `"comma"`, `"semicolon"`. Default is `"space"`.

## Directory Structure

After setup, your working directory should look like this:

```
├── a.out                  # Compiled GCM binary
├── gcm_script.py          # Main Python script
├── format_edgelist.py     # Script for formatting input
├── work.sh                # Shell script executed in the pipeline
├── input.txt              # Example input edgelist file
└── results/               # Example directory for saving results 
```

## Notes

- The `gcm_script.py` script automatically sets up a scratch directory named `gcm_cache_<alpha-numeric code>` to process the input files, run the `work.sh` script, and then the clustering binary. It will also clean up the scratch directory after processing.
- Ensure that `a.out`, `format_edgelist.py`, and `work.sh` are located in the same directory as `gcm_script.py` for the pipeline to work correctly.
- The code in the GCM repository might produce an error if the input filename is longer than 30 characters. Either change the code to increase filename length or ensure the name of the input file is less than 30 characters.
