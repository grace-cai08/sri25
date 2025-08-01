"""
GCM Clustering Pipeline

This script processes an input edgelist file for use with the General Clustering Method (GCM).
It formats the edgelist, runs clustering, and remaps the results for easy interpretation.

The process includes:
1. Formatting the input edgelist by renumbering nodes from 1 to N,
   where N is the number of unique nodes in the graph.
2. Running the GCM algorithm on the formatted edgelist.
3. Remapping the clustering results to the original node indices.

Output is the clustering as produced by the GCM algorithm.

For more details on generalized-modularity-density clustering, refer to https://github.com/prameshsingh/generalized-modularity-density
"""

# Standard library imports
import os
import sys
import shutil
import subprocess
import random
import string
import argparse
from pathlib import Path
from contextlib import contextmanager


def generate_random_string(length=4):
    """
    Generate a random string of alphanumeric characters of the specified length.

    Args:
        length (int): The length of the generated string (default is 4).

    Returns:
        str: A random string of letters and digits.
    """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


@contextmanager
def subprocess_context():
    """
    Context manager for handling subprocess-related exceptions.
    This will capture specific exceptions raised during subprocess execution.

    Yields:
        None
    """
    try:
        yield
    except FileNotFoundError as exc:
        print(f'Process failed because the executable could not be found.\n{exc}')
    except subprocess.CalledProcessError as exc:
        print(f"Process failed: did not return a successful code. Returned {exc.returncode}: {exc}")
    except subprocess.TimeoutExpired as exc:
        print(f"Process timed out.\n{exc}")


def run_work_script(filename):
    """
    Run the `work.sh` script using a given filename as an argument.

    Args:
        filename (str): The file passed as an argument to `work.sh`.
    """
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    path_to_exec = os.path.join(source_dir, "work.sh")

    with subprocess_context():
        subprocess.run(['bash', path_to_exec, filename], check=True)


def run_format_script(filename, sep=None):
    """
    Run the `format_edgelist.py` script to format the input file.

    Args:
        filename (str): Input file to format.
        sep (str): Separator used for formatting. Default is "space".

    Returns:
        tuple: A tuple containing the paths to the formatted file and the key file.
    """
    if sep is None:
        sep = "space"

    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    path_to_exec = os.path.join(source_dir, "format_edgelist.py")

    with subprocess_context():
        subprocess.run(["python", path_to_exec, filename, "--sep", sep])

    filepath_orig = Path(filename)
    return str(filepath_orig.with_stem(filepath_orig.stem + "_formatted")), str(
        filepath_orig.with_stem(filepath_orig.stem + "_key"))


def remap_partition_results(keyfile, formatted_file):
    """
    Remap partition results using a key file and formatted file.

    Args:
        keyfile (str): The key file mapping old IDs to new ones.
        formatted_file (str): The file containing the formatted results.
    """
    result_filename = f'partition_{os.path.basename(formatted_file)}'
    partitions = {}
    mappings = {}

    # Load partitions from result file
    with open(result_filename, 'r') as f:
        i = 0
        for line in f:
            i += 1
            partitions[i] = int(line.strip())

    # Load mappings from key file
    with open(keyfile, 'r') as f:
        for line in f:
            a, b = line.split()
            a, b = int(a), int(b)
            mappings[b] = a

    # Write remapped results
    with open(result_filename, 'w') as f:
        for k, v in partitions.items():
            print(f'{mappings[k]} {v}', file=f)


def _setup_and_enter_scratch(initial_working_directory, input_file):
    """
    Set up a temporary scratch directory and copy the input file to it.

    Args:
        initial_working_directory (str): The starting working directory.
        input_file (str): The input file to be processed.

    Returns:
        tuple: Paths to the scratch directory and the scratch file.
    """
    scratch_directory = os.path.join(initial_working_directory, f"gcm_cache_{generate_random_string()}")
    os.makedirs(scratch_directory)
    scratch_file = os.path.join(scratch_directory, os.path.basename(input_file))
    shutil.copy(input_file, scratch_file)
    os.chdir(scratch_directory)
    return scratch_directory, scratch_file


def _exit_and_cleanup_scratch(output_dir, output_file, initial_working_dir, scratch_directory, formatted_file):
    """
    Cleanup the scratch directory and move the output to the designated directory.

    Args:
        output_dir (str): The directory where output should be saved.
        output_file (str): The name of the output file.
        initial_working_dir (str): The starting working directory.
        scratch_directory (str): The scratch directory used for temporary work.
        formatted_file (str): The formatted file containing the results.
    """
    result_filename = f'partition_{os.path.basename(formatted_file)}'
    output_filepath = os.path.join(output_dir, output_file)
    result_filepath = os.path.join(scratch_directory, result_filename)

    # Copy result file to output directory
    if os.path.exists(result_filepath):
        shutil.copy(result_filepath, output_filepath)
    else:
        print("Error encountered, no result exists")

    # Restore the original working directory and clean up the scratch directory
    os.chdir(initial_working_dir)
    if os.path.exists(scratch_directory):
        shutil.rmtree(scratch_directory)


def run_clustering(filename, chi=0.0, seed=12345):
    """
    Run the clustering algorithm using the compiled `a.out` binary.

    Args:
        filename (str): The input file to cluster.
        chi (float): Chi value to be used in clustering.
        seed (int): Seed for random number generation.
    """
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent

    with subprocess_context():
        subprocess.run([f'{source_dir}/a.out', "2", "5", "2", f"{seed}", f"{chi}", filename], check=True)


def gcm(input_file, chi=0.0, seed=12345, output_dir=None, output_file=None, sep=None):
    """
    Main function to perform GCM (General Clustering Method) on an input file.

    Args:
        input_file (str): Input file for clustering.
        chi (float): Chi value to be used in clustering (default is 0.0).
        seed (int): Seed for random number generation (default is 12345).
        output_dir (str): Directory to save the output (default is None, i.e., current directory).
        output_file (str): Name of the output file (default is "clustering_output.txt").
        sep (str): Separator for the format script (default is None).
    """
    initial_working_directory = os.getcwd()
    if output_dir is None:
        output_dir = initial_working_directory

    if output_file is None:
        output_file = "clustering_output.txt"

    try:
        # Set up scratch space and run the sequence of scripts
        scratch_directory, scratch_file = _setup_and_enter_scratch(initial_working_directory, input_file)
        formatted_file, key_file = run_format_script(os.path.basename(scratch_file), sep=sep)
        run_work_script(os.path.basename(formatted_file))
        run_clustering(os.path.basename(formatted_file), chi, seed)
        remap_partition_results(key_file, formatted_file)
    finally:
        _exit_and_cleanup_scratch(output_dir, output_file, initial_working_directory, scratch_directory, formatted_file)


if __name__ == '__main__':
    # Argument parser setup
    parser = argparse.ArgumentParser(description='Process an input file, run a script, and handle output.')
    parser.add_argument('input_file', type=str, help='Input file name, e.g., file_name.txt')
    parser.add_argument('--output_dir', type=str, help='Directory to save the output file', default=None)
    parser.add_argument('--output_file', type=str, help='Filename for the output file', default=None)
    parser.add_argument('--seed', type=int, help='Random seed for GCM', default=12345)
    parser.add_argument('--chi', type=float, help='Value of Chi', default=0.0)
    parser.add_argument('--sep', help='Value of separator for formatting', choices=["space", "comma", "semicolon"],
                        default="space")

    # Parse arguments and run GCM
    args = parser.parse_args()
    gcm(args.input_file, args.chi, args.seed, args.output_dir, args.output_file, sep=args.sep)
