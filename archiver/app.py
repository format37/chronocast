from google.cloud import bigquery, storage
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BigQueryExporter:
    def __init__(self):
        # Constants
        self.PROJECT_ID = "usavm-334506"
        self.BUCKET_NAME = "rtlm"
        self.DATASET = "rtlm"
        self.TABLE = "channel_transcripts"
        self.LOCAL_PATH = "/tmp/export.parquet"
        self.BLOB_PATH = "exports/channel_transcripts.parquet"
        
        # Initialize clients
        self.bq_client = bigquery.Client(project=self.PROJECT_ID)
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.BUCKET_NAME)
        
    def export_to_parquet(self) -> bool:
        try:
            start_time = datetime.now()
            logger.info("Starting BigQuery export")
            
            # Query all data
            query = f"""
            SELECT * 
            FROM `{self.PROJECT_ID}.{self.DATASET}.{self.TABLE}`
            ORDER BY file_path
            """
            
            df = self.bq_client.query(query).to_dataframe()
            logger.info(f"Retrieved {len(df)} rows from BigQuery")
            
            # Save to temporary file first
            temp_path = f"{self.LOCAL_PATH}.temp"
            df.to_parquet(
                temp_path,
                engine='pyarrow',
                index=False,
                compression='snappy'
            )
            
            # Atomic replace
            os.replace(temp_path, self.LOCAL_PATH)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Export completed in {duration:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False
            
    def upload_to_gcs(self) -> bool:
        try:
            logger.info(f"Uploading {self.LOCAL_PATH} to gs://{self.BUCKET_NAME}/{self.BLOB_PATH}")
            blob = self.bucket.blob(self.BLOB_PATH)
            blob.upload_from_filename(self.LOCAL_PATH)
            logger.info("Upload completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False
            
    def wait_until_next_run(self):
        now = datetime.now()
        next_run = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
            
        wait_seconds = (next_run - now).total_seconds()
        logger.info(f"Waiting {wait_seconds:.0f} seconds until next run at {next_run}")
        time.sleep(wait_seconds)
        
    def run_forever(self):
        logger.info("Starting BigQuery Export Service")
        
        while True:
            try:
                if self.export_to_parquet():
                    if self.upload_to_gcs():
                        logger.info("Export cycle completed successfully")
                    else:
                        logger.error("Upload failed, will retry next cycle")
                else:
                    logger.error("Export failed, will retry next cycle")
                    
                self.wait_until_next_run()
                
            except Exception as e:
                logger.error(f"Unexpected error in run cycle: {str(e)}")
                # Wait 5 minutes before retrying after unexpected error
                time.sleep(300)

if __name__ == "__main__":
    exporter = BigQueryExporter()
    exporter.run_forever()
    