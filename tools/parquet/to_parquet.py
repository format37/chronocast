import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
from collections import defaultdict

def save_transcription_to_parquet(folder_path, output_folder):
    # Dictionary to accumulate data by channel and month
    data_by_channel_month = defaultdict(list)
    
    # Traverse all files and accumulate data
    # for root, _, files in os.walk(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=True):
        dirs.sort()
        files.sort()
        file_counter = 0
        print(f"Processing folder: {root}")
        for file in files:
            if file.endswith('.txt'):
                print(f"Processing file: {file}")
                
                # Extract date, time, and channel information
                file_path = os.path.join(root, file)
                date, time = file.split('_')
                channel_name = os.path.basename(root)
                
                # Convert date to year and month
                year, month, day = date.split('-')
                month_str = f"{year}-{month}"

                # Read transcription text
                with open(file_path, 'r') as f:
                    transcription_text = f.read()

                # Append data to the appropriate channel-month group
                data_by_channel_month[(channel_name, month_str)].append({
                    'date': date,
                    'time': time.split('.')[0],
                    'channel': channel_name,
                    'transcription': transcription_text
                })
            file_counter += 1
            if file_counter >= 10:
                break

    # Save accumulated data to Parquet files, grouped by month and channel
    for (channel_name, month_str), records in data_by_channel_month.items():
        print(f"Saving data for {channel_name} - {month_str}")
        
        # Create DataFrame from accumulated records
        df = pd.DataFrame(records)
        
        # Ensure the output directory exists
        output_channel_folder = os.path.join(output_folder, channel_name)
        os.makedirs(output_channel_folder, exist_ok=True)

        # Write to Parquet file, named by month and channel
        output_file = os.path.join(output_channel_folder, f"{month_str}.parquet")
        table = pa.Table.from_pandas(df)
        pq.write_table(table, output_file)

# Usage
save_transcription_to_parquet('/mnt/hdd0/share/alex/datasets/chronocast/data/transcriptions', './temp')
