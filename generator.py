import os
import json

def create_media_json(root_folder, output_file):
    media_data = {}

    for folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder)

        if os.path.isdir(folder_path):
            media_files = []

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path) and is_media_file(filename):
                    media_files.append({
                        "media": f"https://minhh2792.is-a.dev/mcr/{folder}/{filename}"
                    })

            if media_files:
                media_data[folder] = media_files

    with open(output_file, "w") as json_file:
        json.dump(media_data, json_file, indent=4)

def is_media_file(filename):
    # Check if the file has a media extension (you can customize this based on your file types)
    media_extensions = {".png", ".jpg", ".jpeg", ".gif", ".mp4"}
    return any(filename.lower().endswith(ext) for ext in media_extensions)

# Specify the root folder and output file
root_folder = "./"
output_file = "./medias.json"

# Create the media JSON file
create_media_json(root_folder, output_file)
