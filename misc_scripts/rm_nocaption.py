import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Delete files without an associated ".caption" file.')
    parser.add_argument('--dir_path', type=str, help='The directory path.')
    return parser.parse_args()

TXT_EXTS = ('.caption', '.txt', '.tags', '.tag')

def delete_files_without_caption(dir_path):
    for filename in os.listdir(dir_path):
        if not filename.endswith(TXT_EXTS):
            found_txt = False
            for ext in TXT_EXTS:
                caption_filename = os.path.splitext(filename)[0] + ext
                if os.path.exists(os.path.join(dir_path, caption_filename)):
                    found_txt = True
                    break
            if not found_txt:
                print(os.path.join(dir_path, filename))
                #os.remove(os.path.join(dir_path, filename))

def main():
    args = parse_args()
    delete_files_without_caption(args.dir_path)

if __name__ == '__main__':
    main()
