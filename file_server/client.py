import requests
import os

BASE_URL = "http://127.0.0.1:80"  # Change this if your server is on a different address
API_TOKEN = "your_secret_token"  # This should match the token in the server

headers = {"Authorization": API_TOKEN}
# headers = {"Authorization": f"Bearer {API_TOKEN}"}

def list_files(directory):
    """Lists files in the specified directory."""
    response = requests.get(f"{BASE_URL}/list-files/{directory}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")

def download_file(file_path, save_path):
    """Downloads a file from the server."""
    response = requests.get(f"{BASE_URL}/download-file/{file_path}", headers=headers, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
        print(f"File downloaded: {save_path}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def delete_file(file_path):
    """Deletes a file from the server."""
    response = requests.delete(f"{BASE_URL}/delete-file/{file_path}", headers=headers)
    if response.status_code == 200:
        print("File deleted.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Example usage
if __name__ == "__main__":
    # Replace 'your_directory' with the directory you want to list files from
    print("Listing files...")
    files = list_files('data/audio')
    print(files)

    # Replace 'file_path_on_server' with the file you want to download
    # and 'local_save_path' with the path where you want to save the file
    print("\nDownloading file...")
    download_file('data/audio/TKMFullText.pdf', './TKMFullText.pdf')

    # Replace 'file_path_on_server' with the file you want to delete
    print("\nDeleting file...")
    delete_file('data/audio/TKMFullText.pdf')

print("Done!")
