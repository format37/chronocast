from google.cloud import bigquery
from collections import defaultdict
import pandas as pd
import re

class DehumanizationScorer:
    def __init__(self):
        # Define dehumanization patterns and their weights
        self.patterns = {
            'animalistic': {
                'patterns': [
                    'крыса', 'свинья', 'животное', 'скот', 'стадо',
                    'таракан', 'паразит', 'насекомое', 'зверь', 'тварь',
                    'нечисть', 'гнида', 'козел'
                ],
                'weight': 1.5
            },
            'mechanistic': {
                'patterns': [
                    'биомасса', 'ресурс', 'инструмент', 'механизм',
                    'винтик', 'робот', 'машина', 'материал', 'укры', 'укроп'
                ],
                'weight': 1.2
            },
            'moral_denial': {
                'patterns': [
                    'нелюдь', 'бездушный', 'безнравственный',
                    'аморальный', 'бесчеловечный', 'нацист',
                    'фашист', 'предатель', 'враг народа'
                ],
                'weight': 1.8
            },
            'deindividuation': {
                'patterns': [
                    'они все', 'эти', 'такие', 'подобные',
                    'все они', 'их народ', 'их племя'
                ],
                'weight': 1.0
            }
        }

    def calculate_score(self, text):
        if not isinstance(text, str):
            return 0, {}
            
        text = text.lower()
        scores = defaultdict(int)
        matches = defaultdict(list)
        
        for category, data in self.patterns.items():
            for pattern in data['patterns']:
                count = len(re.findall(r'\b' + re.escape(pattern) + r'\b', text))
                if count > 0:
                    weight = data['weight']
                    scores[category] += count * weight
                    matches[category].append((pattern, count))
        
        # Calculate total score
        total_score = sum(scores.values())
        
        # Normalize by text length (per 1000 words)
        word_count = len(text.split())
        if word_count > 0:
            normalized_score = (total_score / word_count) * 1000
        else:
            normalized_score = 0
            
        return normalized_score, dict(matches)

def analyze_transcripts():
    # Initialize BigQuery client
    client = bigquery.Client(project="usavm-334506")
    
    # Initialize scorer
    scorer = DehumanizationScorer()
    
    # Query to get transcripts
    query = """
    SELECT 
        transcript_id,
        channel,
        transcript_text,
        timestamp,
        file_path
    FROM `usavm-334506.rtlm.channel_transcripts`
    WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    ORDER BY timestamp
    """
    
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
    daily_scores = results_df.groupby(['channel', pd.Grouper(key='timestamp', freq='D')])['dehumanization_score'].mean()
    
    # Print summary statistics
    print("\nAverage Dehumanization Scores by Channel:")
    print(results_df.groupby('channel')['dehumanization_score'].agg(['mean', 'min', 'max']))
    
    # Save detailed results
    results_df.to_csv('dehumanization_analysis.csv', index=False)
    
    return results_df, daily_scores

if __name__ == "__main__":
    results_df, daily_scores = analyze_transcripts()
    
    # Print some example results
    print("\nSample of high-scoring transcripts:")
    high_scores = results_df[results_df['dehumanization_score'] > results_df['dehumanization_score'].mean()]
    print(high_scores[['channel', 'timestamp', 'dehumanization_score', 'matches']].head())
