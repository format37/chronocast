import logging
import requests
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
    