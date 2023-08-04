import argparse
import os
import shutil
import random

def main():
    parser = argparse.ArgumentParser(description='Randomly copy N files from one directory to another.')
    parser.add_argument('input_dir', type=str, help='The source directory.')
    parser.add_argument('output_dir', type=str, help='The destination directory.')
    parser.add_argument('-n', type=int, help='The number of files to copy.')

    args = parser.parse_args()

    all_files = [f for f in os.listdir(args.input_dir) if os.path.isfile(os.path.join(args.input_dir, f))]

    selected_files = random.sample(all_files, args.n)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for file in selected_files:
        shutil.copy(os.path.join(args.input_dir, file), args.output_dir)

if __name__ == "__main__":
    main()
