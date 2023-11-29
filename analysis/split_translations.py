import pandas as pd
import os

def file_to_sentences(filepath):
    """
    Reads a file and splits its content into sentences.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        text = file.read()
        sentences = text.split('.')
        # Include filename and sentence in a tuple
        sentences = [(os.path.basename(filepath), sentence.strip()) 
                     for sentence in sentences if sentence.strip()]
    return sentences

def process_files_in_folder(folder_path, destination_path):
    """
    Processes all text files in a specified folder, 
    splitting their content into sentences and saving 
    the result to a CSV file along with the filename.
    """
    filepaths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]
    all_sentences = []
    for filepath in filepaths:
        sentences = file_to_sentences(filepath)
        all_sentences.extend(sentences)
    df_sentences = pd.DataFrame(all_sentences, columns=['Filename', 'Sentence'])
    csv_filepath = os.path.join(destination_path, 'sentences.csv')
    df_sentences.to_csv(csv_filepath, index=False)
    print(f"Sentences saved to {csv_filepath}")

# Example usage
folder_path = './data/translated/'  # Replace with the path to your folder
destination_path = './data/splitted/'
process_files_in_folder(folder_path, destination_path)
