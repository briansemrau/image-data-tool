
import glob
import argparse
import os

def scan_directory(directory):
    print("Scanning directory", directory)
    for root, dirs, files in os.walk(directory):
        print("Scanning", root)
        for file in files:
            yield os.path.join(root, file)

def main():
    parser = argparse.ArgumentParser(description='Recursively scans a folder for .tag files and deletes the corresponding image if the tag file contains certain tags.')
    parser.add_argument('directory', type=str, help='The directory to scan.')
    parser.add_argument('--whitelist', '-w', type=str, help='Required tags, separated by commas.')
    parser.add_argument('--blacklist', '-b', type=str, help='Forbidden tags, separated by commas.')
    parser.add_argument('--dry', '-d', action='store_true', help='Dry run. Does not delete anything.')
    args = parser.parse_args()

    # TODO FIX: THIS DELETES EVERYTHING
    print("SCRIPT IS BROKEN")
    return

    for file in scan_directory(args.directory):
        if not os.path.exists(file) or file.endswith('.zip'):
            continue
        if not file.endswith(('.png', '.jpg', '.jpeg')):
            discard_file(file)
            continue
        if file.endswith('.tag'):
            tag_string = open(file, 'r').read()
            if args.whitelist:
                if not all(tag.strip() in tag_string for tag in args.whitelist.split(',')):
                    discard_file(file, args.dry)
                    continue
            if args.blacklist:
                if any(tag.strip() in tag_string for tag in args.blacklist.split(',')):
                    discard_file(file, args.dry)
                    continue

def discard_file(file, dry):
    base_name = os.path.splitext(file)[0]

    for f in glob.glob(base_name + ".*"):
        if not dry:
            #os.remove(f)
            print("Deleted", f)
        else:
            print("Would delete", f)

if __name__ == "__main__":
    main()