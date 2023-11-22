import whisper
import time
import logging
import requests
import os
import json
from google.cloud import storage

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

def upload_to_bucket(project_name, local_path, blob_path):
    """Uploads a file to the bucket."""
    BUCKET_NAME = 'rtlm'  # Your Google Cloud Storage bucket name
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)
    logger.info(f"File {local_path} uploaded to {blob_path}.")
    

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
        try:
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
            transcription_filepath = f"/app/data/transcriptions/{project_name}/{transcription_filename}"
            with open(transcription_filepath, "w") as f:
                f.write(transcription)

            local_path = transcription_filepath
            blob_path = f"transcriptions/{project_name}/{transcription_filename}"
            upload_to_bucket(project_name, local_path, blob_path)

            # move file to /app/data/processed
            os.rename(filepath, f"/app/data/processed/{project_name}/{filename}")
        except Exception as e:
            logger.error(f"Error: {e}")
            # create err folder if not exists
            os.makedirs(f"/app/data/processed/{project_name}/err", exist_ok=True)
            # move file to /app/data/processed
            os.rename(filepath, f"/app/data/processed/{project_name}/err/{filename}")

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

        server_files_len_max = 0

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

            if server_files_len > server_files_len_max:
                server_files_len_max = server_files_len

        # wait for 60 seconds
        if server_files_len_max < 2:
            print("Queue is empty. Waiting for 60 sec...")
            time.sleep(60)


if __name__ == "__main__":
    main()
