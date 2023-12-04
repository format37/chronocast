##############################################
# This script lists the directories in a folder:
# data/transcriptions/{project_name}/*.txt
# For each project it reads a list of files that is already in zip file:
# data/archive/{year}_{project_name}.zip
# and appends the files that are not in the zip file.
# Then it waits for one day and repeats the process.
##############################################

import zipfile
import os
import logging
import time
import datetime
from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_to_bucket(local_file_path, destination_blob_name):
    blob_path = f"archive/{destination_blob_name}"
    BUCKET_NAME = 'rtlm'  # Google Cloud Storage bucket name
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    logger.info(f"File {local_file_path} uploaded to {destination_blob_name}.")


def list_files_in_zip(zipfile_path):
    file_list = []
    try:
        # Open the zip file
        with zipfile.ZipFile(zipfile_path, 'r') as zipf:
            file_list = [file_info.filename for file_info in zipf.infolist()]
    except FileNotFoundError:
        logger.error(f"The file {zipfile_path} was not found.")
        return None
    except zipfile.BadZipFile:
        logger.error(f"The file {zipfile_path} is not a valid zip file.")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None
    
    return file_list


def append_to_zip(zipfile_path, files_to_append):
    # Open the zip file in append mode or create a new one if it doesn't exist
    with zipfile.ZipFile(zipfile_path, 'a') as zipf:
        for file in files_to_append:
            # Check if the file exists
            if os.path.exists(file):
                # Add file to zip
                zipf.write(file)
            else:
                logger.error(f"File not found: {file}")


def main():
    data_dir = 'data/transcriptions'
    archive_dir = 'data/archive'
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir, exist_ok=True)
    
    while True:
        logger.info("Starting...")

        archives = []

        projects = os.listdir(data_dir)
        for project in projects:
            logger.info(f"Processing project {project}...")
            project_dir = os.path.join(data_dir, project)
            files = os.listdir(project_dir)
            files = [os.path.join(project_dir, file) for file in files]
            current_year = datetime.datetime.now().strftime('%Y')
            # exclude files that older than current year or earlier than 2 days ago
            files = [
                file for file in files if file.split('/')[-1].split('_')[0].split('-')[0] == current_year or \
                    (datetime.datetime.now() - datetime.datetime.strptime(file.split('/')[-1].split('_')[0], '%Y-%m-%d')).days < 2
                    ]
            logger.info(f"Found {len(files)} files in {project_dir}")

            years_set = {file.split('/')[-1].split('_')[0].split('-')[0] for file in files}
            years_list = list(years_set)
            # Read what files in archive
            for year in years_list:
                logger.info(f"Processing year {year}...")
                archive_folder = os.path.join(archive_dir, f'{year}_{project}.zip')
                # Read files in archive
                files_in_archive = list_files_in_zip(archive_folder)                
                # Exclude files that are already in the archive
                if files_in_archive is not None:
                    logger.info(f"Found {len(files_in_archive)} files in {archive_folder}")
                    files = [file for file in files if file not in files_in_archive]
                logger.info(f"Found {len(files)} files to append to {archive_folder}")
                # Append files to archive
                append_to_zip(archive_folder, files)
                archives.append(archive_folder)

        # Upload files to GCS
        for archive in archives:
            logger.info(f"Uploading {archive} to GCS...")
            upload_to_bucket(archive, archive.split('/')[-1])

        logger.info("Sleeping for 1 day...")
        time.sleep(86400)


if __name__ == '__main__':
    main()
