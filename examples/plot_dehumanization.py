import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def main():
    # Read the CSV file
    df = pd.read_csv('dehumanization_analysis.csv')
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create daily averages
    daily_scores = df.groupby([df['timestamp'].dt.date, 'channel'])['dehumanization_score'].mean().reset_index()
    
    # Set up the plot style
    plt.style.use('seaborn')
    plt.figure(figsize=(15, 8))
    
    # Create line plot for each channel
    channels = daily_scores['channel'].unique()
    colors = sns.color_palette("husl", len(channels))
    
    for channel, color in zip(channels, colors):
        channel_data = daily_scores[daily_scores['channel'] == channel]
        plt.plot(channel_data['timestamp'], 
                channel_data['dehumanization_score'], 
                marker='o', 
                linestyle='-', 
                label=channel,
                color=color,
                markersize=4)
    
    # Customize the plot
    plt.title('Dehumanization Score Trends by Channel', fontsize=14, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Dehumanization Score', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Channel', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('dehumanization_trends.png', dpi=300, bbox_inches='tight')
    print("Plot saved as dehumanization_trends.png")

    # Print summary statistics
    print("\nSummary Statistics by Channel:")
    summary = df.groupby('channel')['dehumanization_score'].agg(['mean', 'std', 'min', 'max'])
    print(summary.round(3))

if __name__ == "__main__":
    main()