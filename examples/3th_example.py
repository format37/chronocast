from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client(project="usavm-334506")  # Replace with your project ID

# Construct a reference to the table
table_ref = client.get_table("usavm-334506.rtlm.channel_transcripts")

# Get the table schema
schema = table_ref.schema

# Print field names and their types
print("Table fields:")
for field in schema:
    print(f"{field.name}: {field.field_type}")


# Query the table
# query_job = client.query(f"SELECT * FROM `{table_ref}` LIMIT 1") # Replace with your query
query_job = client.query(f"SELECT * FROM `{table_ref}` WHERE file_path = '2024-12-20_14-42-54.mp3' LIMIT 10") # Replace with your query

# Iterate over the results and print them
for row in query_job:
    print(row.transcript_text)

# # Query to get the text from the last record
# last_record_query = client.query("""
#     SELECT text FROM `usavm-334506.rtlm.channel_transcripts` 
#     ORDER BY file_path DESC 
#     LIMIT 1
# """)

# # Get and print the text
# for row in last_record_query:
#     print(row.text)