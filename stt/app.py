import whisper
import os
import time
import pandas as pd
import logging
import requests
import os

# Init logging with level INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8054"  # Change this if your server is on a different address
API_TOKEN = "your_secret_token"  # This should match the token in the server
headers = {"Authorization": API_TOKEN}

def list_files(directory):
    """Lists files in the specified directory."""
    response = requests.get(f"{BASE_URL}/list-files/{directory}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")

def download_file(file_path, save_path):
    """Downloads a file from the server."""
    response = requests.get(f"{BASE_URL}/download-file/{file_path}", headers=headers, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
        print(f"File downloaded: {save_path}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def delete_file(file_path):
    """Deletes a file from the server."""
    response = requests.delete(f"{BASE_URL}/delete-file/{file_path}", headers=headers)
    if response.status_code == 200:
        print("File deleted.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def main():
    model_name = "large"
    logger.info(f"Loading the model {model_name}...")
    model = whisper.load_model(model_name, download_root='/app/cache')

    while(True):
        # Download the file
        path = 'data/audio/ORT'
        files = list_files(path)
        logger.info(f"Found {len(files)} files in {path}")
        server_files_len = len(files)
        counter = 0
        for file in files:
            if counter == len(files)-1:
                print("counter:", counter, "files:", len(files))
                break            
            file_path = f'{path}/{file}'
            print("\nDownloading file: ", file_path)
            download_file(file_path, f'/app/data/audio/{file}')
            delete_file(file_path)        
            counter += 1
            break # TODO: You may need to remove this break


        # get list of files in /app/data/audio sorted ascending
        files = os.listdir("/app/data/audio")
        files.sort()
        logger.info(f"Found {len(files)} files in /app/data/audio")

        iterator = 0

        # iterate files
        for file in files:
            # get file name
            filename = os.path.basename(file)
            # get file path
            filepath = os.path.join("/app/data/audio", file)
            logger.info(f"Processing file {filename}...")
            result = model.transcribe(
                filepath,
                language="ru",
                temperature=0.8,
                prompt="Аудиозапись с телевизора"
            )
            # print(result["text"])

            # transcription = filename
            transcription = result["text"]
            logger.info(f"Transcription length: {len(transcription)}")
            # save transcription to file
            transcription_filename = filename.replace(".mp3", ".txt")
            with open(f"/app/data/transcriptions/{transcription_filename}", "w") as f:
                f.write(transcription)

            # move file to /app/data/processed
            os.rename(filepath, f"/app/data/processed/{filename}")

            iterator += 1
            # break before the last file
            if iterator >= len(files)-1:
            # if iterator >= 2:
                break

        # wait for 600 seconds
        if server_files_len < 2:
            print("Queue is empty. Waiting for 10 minutes...")
            time.sleep(600)


if __name__ == "__main__":
    main()
