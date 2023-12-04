import pandas as pd
import logging
import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def clustering(df, n_clusters):
    # df["embedding"] = df.embedding.apply(literal_eval).apply(np.array)  # convert string to numpy array
    matrix = np.vstack(df.embedding.values)
    logger.info(f"Matrix shape: {matrix.shape}")

    # 1. Find the clusters using K-means
    # We show the simplest use of K-means. 
    # You can pick the number of clusters that fits your use case best.
    # n_clusters = 4
    logger.info(f"Clustering into {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", random_state=42)
    kmeans.fit(matrix)
    labels = kmeans.labels_
    df["Cluster"] = labels

    # df.groupby("Cluster").Score.mean().sort_values()    
    return df, matrix


# Defining a custom function to convert the string representation to a NumPy array
def convert_to_array(embedding_str):
    # Removing the square brackets and splitting the string by space to get the individual elements
    elements = embedding_str[1:-1].split()
    # Converting the elements to floats and creating a NumPy array
    return np.array([float(e) for e in elements])


def plot_clusters(df, matrix, legend_append_values=None):

    channels_instead_of_clusters = True

    logger.info("Plotting clusters...")
    tsne = TSNE(n_components=2, perplexity=15, random_state=42, init="random", learning_rate=200)
    vis_dims2 = tsne.fit_transform(matrix)

    x = [x for x, y in vis_dims2]
    y = [y for x, y in vis_dims2]
    
    # Add name column
    # df["name"] = df["source"].apply(lambda x: x.split("_")[0])
    df["name"] = df["Filename"].apply(lambda x: x.split("_")[0])
    
    # Add name_id column
    names = df["name"].unique()
    name_to_id = {name: i for i, name in enumerate(names)}
    df["name_id"] = df["name"].map(name_to_id)

    colors = [
        "purple", 
        "green", 
        "blue", 
        "red", 
        "orange", 
        "yellow", 
        "pink", 
        "brown", 
        "gray", 
        "black", 
        "cyan", 
        "magenta"
        ]
    # colors = colors[:len(np.unique(df.Cluster))]
    # colors = plt.get_cmap("tab10").colors
    
    # Initialize subplot
    fig = make_subplots(rows=1, cols=1)
    
    if channels_instead_of_clusters:
        colors = {name_id: color for name_id, color in zip(df["name_id"].unique(), colors)}
        for name_id in df["name_id"].unique():
            color = colors[name_id]
            name = names[name_id]
            
            xs = np.array(x)[df["name_id"] == name_id] 
            ys = np.array(y)[df["name_id"] == name_id]
            texts = df[df["name_id"] == name_id]['Sentence'].values

            name_percentage = (df["name_id"] == name_id).mean() * 100

            fig.add_trace(
                go.Scatter(
                x=xs, y=ys,  
                mode='markers',
                marker=dict(color=color, size=5),
                hovertext=texts,
                hoverinfo='text',
                name=f'{name} ({name_percentage:.2f}%)',
                )
            )

            avg_x = xs.mean()
            avg_y = ys.mean()

            fig.add_trace(
                go.Scatter(
                x=[avg_x], y=[avg_y],
                mode='markers',
                marker=dict(color=color, size=10, symbol='x'),
                name=f'Avg {name}',
                hoverinfo='name'
                )
            )

        fig.update_layout(
        showlegend=True, 
        title_text="Clusters visualized in 2D by name using t-SNE"
        )
        fig.show()

    else: # clusters    
        colors = ["purple", "green", "red", "blue", "orange", "yellow", "pink", "brown", "gray", "black", "cyan", "magenta"]
        colors = colors[:len(np.unique(df.Cluster))]
        cluster_sizes = df.Cluster.value_counts(normalize=True).sort_values(ascending=False)
        for category in cluster_sizes.index:
            color = colors[category]
            xs = np.array(x)[df.Cluster == category]
            ys = np.array(y)[df.Cluster == category]
            texts = df[df.Cluster == category]['Sentence'].values  # Get the text for each point in this cluster

            cluster_percentage = cluster_sizes[category] * 100  # cluster_sizes is already normalized

            # Append values to the legend
            if legend_append_values is not None:
                legend_append = f', {legend_append_values[category]}'
            else:
                legend_append = ''

            # Add scatter plot to subplot
            fig.add_trace(
                go.Scatter(
                    x=xs, y=ys, 
                    mode='markers',
                    marker=dict(color=color, size=5),
                    hovertext=texts,  # Display the text when hovering over a point
                    hoverinfo='text',  # Show only the hovertext
                    name=f'Cluster {category} ({cluster_percentage:.2f}%)' + legend_append,
                )
            )

            avg_x = xs.mean()
            avg_y = ys.mean()

            # Add marker for average point to subplot
            fig.add_trace(
                go.Scatter(
                    x=[avg_x], y=[avg_y],
                    mode='markers',
                    marker=dict(color=color, size=10, symbol='x'),
                    name=f'Avg Cluster {category}',
                    hoverinfo='name'
                )
            )

        fig.update_layout(showlegend=True, title_text="Clusters identified visualized in language 2d using t-SNE")
        fig.show()


def main():
    n_clusters = 4
    # Load embeddings
    logger.info('Loading embeddings...')
    df = pd.read_csv('data/embeddings.csv')
    # df = pd.read_csv('local_conversations_embeddings.csv')
    logger.info(f'0. Number of sentences: {len(df)}')

    # Drop records that shorter than 10 characters
    logger.info('Dropping records that shorter than 100 characters...')
    df = df[df['Sentence'].str.len() > 100]
    logger.info(f'1. Number of sentences: {len(df)}')

    filter = [
        'transcript',
        'subtit',
    ]
    # Drop records, that contains filter words
    logger.info('Dropping records, that contains filter words...')
    df = df[~df['Sentence'].str.contains('|'.join(filter))]
    logger.info(f'2. Number of sentences: {len(df)}')

    # Reloading the original DataFrame from the CSV file
    # df = pd.read_csv('embeddings.csv')
    # Applying the custom conversion function to the 'embedding' column
    df['embedding'] = df['embedding'].apply(convert_to_array)

    # Clustering
    logger.info('Clustering...')
    df, matrix = clustering(df, n_clusters=n_clusters)

    # Summarize topics
    # legend = topic_samples_central(df, matrix, openai_key=openai_key, n_clusters=n_clusters, rev_per_cluster=10)
    # Fake legend
    legend = ['Topic 0', 'Topic 1', 'Topic 2', 'Topic 3']
    # Plot clusters
    plot_clusters(df, matrix, legend_append_values=legend)

    logger.info('Done.')


if __name__ == "__main__":
    main()
