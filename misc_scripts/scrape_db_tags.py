import argparse
import os
import requests
import json

def extract_image_id(image_file):
    return os.path.splitext(image_file)[0].split('_')[1]

def process_image_file(directory, image_file):
    tag_file = os.path.join(directory, f'{os.path.splitext(image_file)[0]}.tag')
    if os.path.exists(tag_file):
        return

    base_url = 'https://safebooru.donmai.us/posts'
    headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

    try:
        image_id = extract_image_id(image_file)
    except:
        print(f'Error extracting image id from file: {image_file}')
        return
    if image_id == '':
        print(f'No image id found for file: {image_file}')
        return

    response = requests.get(f'{base_url}/{image_id}.json', headers=headers)

    if not response.status_code == 200:
        print(f'Error fetching tags for image: {image_id}, status code: {response.status_code}')
        return

    data = json.loads(response.text)

    character = data['tag_string_character']
    tags = ', '.join(data['tag_string_general'].split(' '))
    prompt = f'{character}, {tags}' if character != '' else tags

    with open(tag_file, 'w') as f:
        f.write(prompt)

def scan_directory(directory):
    print("Scanning directory", directory)
    for root, dirs, files in os.walk(directory):
        if root.endswith("mask"):
            continue
        print("Scanning", root)
        for file in files:
            yield root, file

def main(directory):
    for directory, file in scan_directory(directory):
        process_image_file(directory, file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape tags for images.')
    parser.add_argument('directory', type=str, help='The directory containing the images.')
    args = parser.parse_args()
    main(**args.__dict__)
