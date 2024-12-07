import whisper
import time
import os
import json
from datetime import datetime, timezone
import uuid
from google.cloud import bigquery
from bucket import (
    list_files, 
    download_file,
    delete_file,
    logger
)

def extract_channel_and_filename(file_path):
    """
    Extract channel and filename from a file path of format '.../channel/filename.extension'
    Returns tuple of (channel, filename)
    """
    # Split the path and get the last two components
    parts = file_path.split('/')
    channel = parts[-2]  # Second to last component is the channel
    filename = parts[-1]  # Last component is the filename
    return channel, filename

def parse_timestamp_from_filename(filename):
    """
    Parse timestamp from filename of format 'YYYY-MM-DD_HH-MM-SS.extension'
    Returns datetime object in UTC
    """
    # Remove file extension
    timestamp_str = os.path.splitext(filename)[0]
    # Parse timestamp
    dt = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')
    return dt.replace(tzinfo=timezone.utc)

def upload_to_bigquery(transcript_data, table_id):
    """
    Upload a single transcript record to BigQuery
    """
    client = bigquery.Client()
    
    # Define the table schema
    schema = [
        bigquery.SchemaField("transcript_id", "STRING"),
        bigquery.SchemaField("channel", "STRING"),
        bigquery.SchemaField("transcript_text", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("file_path", "STRING"),
        bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP")
    ]
    
    # Get the table reference
    table = client.get_table(table_id)
    
    # Prepare the rows to insert
    rows_to_insert = [transcript_data]
    
    # Insert the rows
    errors = client.insert_rows(table, rows_to_insert)
    
    if errors:
        logger.error(f"Encountered errors while inserting into BigQuery: {errors}")
        raise Exception(f"BigQuery insert failed: {errors}")
    else:
        logger.info(f"Successfully uploaded transcript to BigQuery: {transcript_data['transcript_id']}")

def transcribe(project, model, bq_table_id):
    project_name = project['name']
    # get list of files in /app/data/audio sorted ascending
    files = os.listdir(f"/app/data/audio/{project_name}")
    files.sort()
    logger.info(f"Found {len(files)} files in /app/data/audio/{project_name}")

    for file in files:
        filename = os.path.basename(file)
        filepath = os.path.join(f"/app/data/audio/{project_name}", file)
        logger.info(f"Processing file {filename}...")
        
        try:
            # Perform transcription
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

            transcription = result["text"]
            logger.info(f"Transcription length: {len(transcription)}")
            
            # Save transcription to file
            transcription_filename = filename.replace(".mp3", ".txt")
            transcription_filepath = f"/app/data/transcriptions/{project_name}/{transcription_filename}"
            with open(transcription_filepath, "w") as f:
                f.write(transcription)

            # Extract channel and prepare BigQuery record
            channel, original_filename = extract_channel_and_filename(filepath)
            timestamp = parse_timestamp_from_filename(filename)
            
            # Prepare the record for BigQuery
            bq_record = {
                'transcript_id': str(uuid.uuid4()),
                'channel': channel,
                'transcript_text': transcription,
                'timestamp': timestamp,
                'file_path': original_filename,
                'ingestion_timestamp': datetime.now(timezone.utc)
            }
            
            # Upload to BigQuery
            upload_to_bigquery(bq_record, bq_table_id)

            # Move file to processed directory
            os.rename(filepath, f"/app/data/processed/{project_name}/{filename}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            os.makedirs(f"/app/data/processed/{project_name}/err", exist_ok=True)
            os.rename(filepath, f"/app/data/processed/{project_name}/err/{filename}")
            
            if os.path.getsize(f"/app/data/processed/{project_name}/err/{filename}") > 3000:
                logger.info(f"File size is more than 3Kb. Restarting the container...")
                exit()

def main():
    # Create necessary directories
    os.makedirs(f"/app/data/transcriptions", exist_ok=True)
    os.makedirs(f"/app/data/processed", exist_ok=True)

    # Read config from json
    with open("config.json") as f:
        config = json.load(f)

    logger.info(f"Found {len(config)} projects in config.json:\n{config}")

    # BigQuery table ID
    bq_table_id = "usavm-334506.rtlm.channel_transcripts"

    model_name = "large"
    logger.info(f"Loading the model {model_name}...")
    model = whisper.load_model(model_name, download_root='/app/cache')

    while True:
        server_files_len_max = 0

        for project_name, project in config.items():
            # Create project-specific directories
            os.makedirs(f"/app/data/transcriptions/{project_name}", exist_ok=True)
            os.makedirs(f"/app/data/processed/{project_name}", exist_ok=True)

            BASE_URL = project["BASE_URL"]
            headers = {"Authorization": project["API_TOKEN"]}

            # Download and process files
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
                os.makedirs(f'/app/data/audio/{project_name}', exist_ok=True)
                logger.info(f"Downloading file: {file_path}")
                download_file(file_path, f'/app/data/audio/{project_name}/{file}', BASE_URL, headers)
                transcribe(project, model, bq_table_id)
                delete_file(file_path, BASE_URL, headers)
                counter += 1

            if server_files_len > server_files_len_max:
                server_files_len_max = server_files_len

        # wait for 60 seconds if queue is empty
        if server_files_len_max < 2:
            print("Queue is empty. Waiting for 60 sec...")
            time.sleep(60)

if __name__ == "__main__":
    main()