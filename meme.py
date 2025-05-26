import os
import requests
import urllib.parse
import yaml
import logging
import time
import validators
from shutil import copyfile

logging.basicConfig(level=logging.INFO, format='%(message)s')
# NOTE
# For now™, only the top most ID of a trigger is registered.
# Importing and merging are highly discouraged.

def is_valid_url(url):
    return validators.url(url, strict_query=False) # Cho phép vượt qua validation khi query chết
    # Most likely unsafe practice but for now it works

def create_folders(ids):
    created_folders = 0
    # Flatten the list of IDs
    flat_ids = [id for sublist in ids for id in sublist]
    for folder_id in flat_ids:
        folder_name = str(folder_id)
        try:
            os.makedirs(folder_name, exist_ok=True)
            created_folders += 1
            logging.info(f'[CREATE] Created folder ({folder_id}): .\\{folder_name}')
        except OSError as e:
            logging.error(f'[CREATE] Created folder ({folder_id}): .\\{folder_name}: {e}')

    return created_folders

def update_res_value(file_path, data, downloaded_ids):
    with open(file_path, 'r+', encoding='utf-8') as file:
        current_data = yaml.safe_load(file)
        file.seek(0)
        file.truncate()

        for key, value in current_data.items():
            folder_id = value[0]['id']
            if folder_id in downloaded_ids:
                folder_name = str(folder_id)
                for item in value:
                    media_name = get_media_name(item['res']) # Used new function to better work with proxied URLs
                    new_res_value = f'https://minhh2792.moe/mcr/{folder_id}/{media_name}'
                    item['res'] = new_res_value
                    logging.info(f'[UPDATE] Updated "res" value for ID: {folder_id}, File: {media_name}')

        yaml.dump(current_data, file, default_flow_style=False, allow_unicode=True)

def get_media_name(url):
    # Encode the URL properly to handle special characters
    parsed = urllib.parse.urlparse(urllib.parse.unquote(url))
    if '?' in url:
        # If it's a proxied URL, parse the actual URL after the '?'
        actual_url = parsed.query
        return os.path.basename(urllib.parse.urlparse(actual_url).path)
    return os.path.basename(parsed.path)

def download_media(data, downloaded_ids):
    total_size = sum(len(value) for value in data.values())
    downloaded_size = 0
    total_files = 0

    for key, value in data.items():
        folder_id = value[0]['id']
        folder_name = str(folder_id)
        created_files = 0

        # Kiểm tra xem ID có URL hợp lệ không
        if not all(is_valid_url(item['res']) for item in value):
            logging.error(f'[ERROR] ID: {folder_id} contains invalid URL(s). Skipping folder creation.')
            continue

        for item in value:
            total_files += 1
            url = item['res']

            media_name = get_media_name(url) # Used new function to better work with proxied URLs
            media_path = os.path.join(folder_name, media_name)

            try:
                start_time = time.time()
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(media_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                created_files += 1
                logging.info(f'[DOWNLOAD] ID: {folder_id}, File: {media_name}, COMPLETED!!!')
            except requests.exceptions.RequestException as e:
                logging.error(f'[ERROR] ID: {folder_id}, Downloading {media_name}: {e}')

        downloaded_ids.add(folder_id)

    # Report at the end
    logging.info(f'\n[REPORT] Total IDs created: {len(data)}')
    logging.info(f'[REPORT] Total files downloaded: {total_files}')
    
    return downloaded_ids

def main():
    file_path = 'patched.yml'
    copyfile(file_path, 'patched_copy.yml')

    with open('patched_copy.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    # Get all IDs from each trigger's responses
    ids = [[item['id'] for item in value] for value in data.values()]
    created_folders = create_folders(ids)
    
    downloaded_ids = set()
    
    if created_folders > 0:
        downloaded_ids = download_media(data, downloaded_ids)
    else:
        logging.error('[ERROR] No folders were created. Aborting download.')

    update_res_value('patched_copy.yml', data, downloaded_ids)

if __name__ == "__main__":
    main()