import argparse
import os
import zipfile

def extract_zip(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if input_dir.endswith(".zip"):
        with zipfile.ZipFile(input_dir, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        return
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.zip'):
                zip_file = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(output_dir)
                except zipfile.BadZipFile:
                    print("Bad zip file: " + zip_file)
                    continue

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recursively extract all zip files into a flat output directory')
    parser.add_argument('input_dir', help='Input directory to search for zip files')
    parser.add_argument('output_dir', help='Output directory to extract zip files into')
    args = parser.parse_args()

    extract_zip(args.input_dir, args.output_dir)
