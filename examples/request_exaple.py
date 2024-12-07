from google.cloud import bigquery
from datetime import datetime, timedelta

def query_transcripts(
    project_id="usavm-334506",
    channel=None,
    start_date=None,
    end_date=None,
    text_contains=None
):
    """
    Query transcripts with various filters
    
    Args:
        project_id: GCP project ID
        channel: Specific channel to filter by
        start_date: Start date for filtering (datetime object)
        end_date: End date for filtering (datetime object)
        text_contains: Text to search for in transcript_text
    """
    client = bigquery.Client(project=project_id)
    
    # Start building the query
    query = """
    SELECT
        transcript_id,
        channel,
        transcript_text,
        timestamp,
        file_path,
        ingestion_timestamp
    FROM `usavm-334506.rtlm.channel_transcripts`
    WHERE 1=1
    """
    
    # Add filters if provided
    if channel:
        query += f"\nAND channel = '{channel}'"
        
    if start_date:
        query += f"\nAND timestamp >= '{start_date.strftime('%Y-%m-%d')}'"
        
    if end_date:
        query += f"\nAND timestamp < '{end_date.strftime('%Y-%m-%d')}'"
        
    if text_contains:
        query += f"\nAND LOWER(transcript_text) LIKE LOWER('%{text_contains}%')"
    
    query += "\nORDER BY timestamp DESC"
    
    # Run the query
    query_job = client.query(query)
    
    return query_job.result()

def main():
    # Example 1: Query specific channel for today
    print("\nExample 1: Today's transcripts for specific channel")
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    filter = "завтра"
    results = query_transcripts(
        channel="ORT",
        start_date=today,
        end_date=tomorrow,
        text_contains=filter
    )
    for row in results:
        text = row.transcript_text
        # find the place of that has a filter word
        start = text.lower().find(filter)
        # find the previous dot
        prev_dot = text.rfind(".", 0, start)
        # find the next dot
        next_dot = text.find(".", start)
        cropped_text = text[prev_dot+1:next_dot+1]

        print(f"ID: {row.transcript_id}, Time: {row.timestamp}, Text: ...{cropped_text}...")

if __name__ == "__main__":
    main()
    