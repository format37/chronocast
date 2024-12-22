##############################################
# This script lists the directories in a folder:
# data/transcriptions/{project_name}/*.txt
# For each project it reads a list of files that is already in zip file:
# data/archive/{year}_{project_name}.zip
# and appends the files that are not in the zip file.
# Then it waits for one day and repeats the process.
##############################################

import os
import logging
import time
import datetime
from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_to_bucket(local_file_path, destination_blob_name):
    BUCKET_NAME = 'rtlm'  # Google Cloud Storage bucket name
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    logger.info(f"File {local_file_path} uploaded to {destination_blob_name}.")


def main():
    data_dir = 'data/parquet'
    
    while True:
        logger.info("Starting...")
        
        # Get all projects (subdirectories) in the parquet directory
        projects = os.listdir(data_dir)
        
        for project in projects:
            logger.info(f"Processing project {project}...")
            parquet_file = os.path.join(data_dir, project, f"{project}.parquet")
            
            if os.path.exists(parquet_file):
                # Upload to GCS using the same path structure
                destination_path = f"parquet/{project}/{project}.parquet"
                logger.info(f"Uploading {parquet_file} to GCS...")
                upload_to_bucket(parquet_file, destination_path)
            else:
                logger.error(f"Parquet file not found: {parquet_file}")

        # Calculate time until next run (23:30)
        now = datetime.datetime.now()
        next_run = now.replace(hour=23, minute=30, second=0, microsecond=0)
        if now >= next_run:
            next_run += datetime.timedelta(days=1)
        
        sleep_seconds = (next_run - now).total_seconds()
        logger.info(f"Sleeping until {next_run.strftime('%Y-%m-%d %H:%M:%S')}...")
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()
