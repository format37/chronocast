import whisper
import os
import time
# import pandas as pd
import logging
import requests
import os
import json

# Init logging with level INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BASE_URL = os.environ.get("BASE_URL", "")
# API_TOKEN = os.environ.get("API_TOKEN", "")
# headers = {"Authorization": API_TOKEN}

def list_files(directory, BASE_URL, headers):
    """Lists files in the specified directory."""
    response = requests.get(f"{BASE_URL}/list-files/{directory}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        # print(f"Error: {response.status_code}, {response.text}")
        logger.error(f"Error: {response.status_code}, {response.text}")

def download_file(file_path, save_path, BASE_URL, headers):
    """Downloads a file from the server."""
    response = requests.get(f"{BASE_URL}/download-file/{file_path}", headers=headers, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
        # print(f"File downloaded: {save_path}")
        logger.info(f"File downloaded: {save_path} from {BASE_URL}")
    else:
        # print(f"Error: {response.status_code}, {response.text}")
        logger.error(f"Error: {response.status_code}, {response.text}")

def delete_file(file_path, BASE_URL, headers):
    """Deletes a file from the server."""
    response = requests.delete(f"{BASE_URL}/delete-file/{file_path}", headers=headers)
    if response.status_code == 200:
        # print("File deleted.")
        logger.info(f"File deleted: {file_path} at {BASE_URL}")
    else:
        # print(f"Error: {response.status_code}, {response.text}")
        logger.error(f"Error: {response.status_code}, {response.text}")

def transcribe(project, model):
    project_name = project['name']
    # get list of files in /app/data/audio sorted ascending
    files = os.listdir(f"/app/data/audio/{project_name}")
    files.sort()
    logger.info(f"Found {len(files)} files in /app/data/audio/{project_name}")

    # iterator = 0

    # iterate files
    for file in files:
        # get file name
        filename = os.path.basename(file)
        # get file path
        filepath = os.path.join(f"/app/data/audio/{project_name}", file)
        logger.info(f"Processing file {filename}...")
        if project['language'] == '':
            result = model.transcribe(
                filepath,            
                temperature=0.8,
                prompt=project['prompt']
            )
        else:
            result = model.transcribe(
                filepath,            
                temperature=0.8,
                language=project['language'],
                prompt=project['prompt']
            )
        # language="ru",
        # prompt="Аудиозапись с телевизора"
        # print(result["text"])

        # transcription = filename
        transcription = result["text"]
        logger.info(f"Transcription length: {len(transcription)}")
        # save transcription to file
        transcription_filename = filename.replace(".mp3", ".txt")
        with open(f"/app/data/transcriptions/{project_name}/{transcription_filename}", "w") as f:
            f.write(transcription)

        # move file to /app/data/processed
        os.rename(filepath, f"/app/data/processed/{project_name}/{filename}")

        # iterator += 1
        # break before the last file
        # if iterator >= len(files)-1:
        # if iterator >= 2:
        #     break

def main():
    # create folder /app/data/transcriptions/ if not exists
    os.makedirs(f"/app/data/transcriptions", exist_ok=True)
    # create folder /app/data/processed/ if not exists
    os.makedirs(f"/app/data/processed", exist_ok=True)

    # Read config from json
    with open("config.json") as f:
        config = json.load(f)

    logger.info(f"Found {len(config)} projects in config.json:\n{config}")

    model_name = "large"
    logger.info(f"Loading the model {model_name}...")
    model = whisper.load_model(model_name, download_root='/app/cache')

    while(True):

        server_files_len_min = 2

        for project_name, project in config.items():

            # create folder /app/data/transcriptions/{project} if not exists
            os.makedirs(f"/app/data/transcriptions/{project_name}", exist_ok=True)
            # create folder /app/data/processed/{project} if not exists
            os.makedirs(f"/app/data/processed/{project_name}", exist_ok=True)

            # project = os.environ.get("PROJECT", "")
            # project_name = key
            BASE_URL = project["BASE_URL"]
            # API_TOKEN = value["API_TOKEN"]
            headers = {"Authorization": project["API_TOKEN"]}

            # Download the file
            path = f'data/audio/{project_name}'
            files = list_files(path, BASE_URL, headers)
            logger.info(f"Found {len(files)} files in {path}")
            server_files_len = len(files)
            counter = 0
            for file in files:
                if counter == len(files)-1:
                    print("counter:", counter, "files:", len(files))
                    break            
                file_path = f'{path}/{file}'
                print("\nDownloading file: ", file_path)
                download_file(file_path, f'/app/data/audio/{project_name}/{file}', BASE_URL, headers)
                transcribe(project, model)
                delete_file(file_path, BASE_URL, headers)
                counter += 1

            if server_files_len < server_files_len_min:
                server_files_len_min = server_files_len

        # wait for 600 seconds
        if server_files_len_min < 2:
            print("Queue is empty. Waiting for 10 minutes...")
            time.sleep(600)


if __name__ == "__main__":
    main()
