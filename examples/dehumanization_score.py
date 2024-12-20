from google.cloud import bigquery
import pandas as pd
import re
from dehumanization_words import words as patterns

class DehumanizationScorer:
    def __init__(self):
        self.patterns = patterns

    def calculate_score(self, text):
        if not isinstance(text, str):
            return 0, {}
            
        text = text.lower()
        matches = []
        
        for pattern in self.patterns:
            count = len(re.findall(r'\b' + re.escape(pattern) + r'\b', text))
            if count > 0:
                matches.append((pattern, count))
        
        total_count = sum(count for _, count in matches)
        return total_count, dict(matches)

def analyze_transcripts(start_date=None, end_date=None, group_by='D'):
    # Initialize BigQuery client
    client = bigquery.Client(project="usavm-334506")
    
    # Initialize scorer
    scorer = DehumanizationScorer()
    
    # Query to get transcripts with date filter
    query = """
    SELECT 
        transcript_id,
        channel,
        transcript_text,
        timestamp,
        file_path
    FROM `usavm-334506.rtlm.channel_transcripts`
    WHERE 1=1
    """
    if start_date:
        query += f" AND DATE(timestamp) >= '{start_date}'"
    if end_date:
        query += f" AND DATE(timestamp) <= '{end_date}'"
    query += " ORDER BY timestamp"
    
    # Run query and convert to pandas DataFrame
    df = client.query(query).to_dataframe()
    
    # Calculate scores for each transcript
    results = []
    for _, row in df.iterrows():
        score, matches = scorer.calculate_score(row['transcript_text'])
        
        results.append({
            'transcript_id': row['transcript_id'],
            'channel': row['channel'],
            'timestamp': row['timestamp'],
            'dehumanization_score': score,
            'matches': matches,
            'file_path': row['file_path']
        })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Calculate average scores by channel and date
    daily_scores = results_df.groupby(['channel', pd.Grouper(key='timestamp', freq=group_by)])['dehumanization_score'].mean()
    
    # Print summary statistics
    print("\nAverage Dehumanization Scores by Channel:")
    print(results_df.groupby('channel')['dehumanization_score'].agg(['mean', 'min', 'max']))
    
    # Save detailed results
    results_df.to_csv('dehumanization_analysis.csv', index=False)
    
    return results_df, daily_scores

if __name__ == "__main__":
    results_df, daily_scores = analyze_transcripts(
        start_date='2024-12-01',
        end_date='2024-12-10',
        group_by='D' # H - hours / D - days / M - months / Y - years
    )
    
    # Print some example results
    print("\nSample of high-scoring transcripts:")
    high_scores = results_df[results_df['dehumanization_score'] > results_df['dehumanization_score'].mean()]
    print(high_scores[['channel', 'timestamp', 'dehumanization_score', 'matches']].head())
