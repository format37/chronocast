import os
import datetime

# Set the directory where the folders are located
base_directory = '../data/transcriptions/'  # Replace with your directory path
destination_directory = './data/concatenated/'  # Replace with your directory path

# Folder names
folders = ["belarusone", "oneplusone", "ORT", "russiaone"]

# Get today's date in the required format
today = datetime.datetime.now().strftime("%Y-%m-%d")
# minus day
today = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
print(today)

# Function to read and concatenate files from a folder
def concatenate_files(folder):
    concatenated_content = ""
    files = os.listdir(os.path.join(base_directory, folder))
    # sort
    files.sort()
    for file in files:
        if file.startswith(today) and file.endswith(".txt"):
            with open(os.path.join(base_directory, folder, file), 'r') as f:
                concatenated_content += f.read() + "\n"
    return concatenated_content

# Process each folder and create a new file with concatenated content
for folder in folders:
    content = concatenate_files(folder)
    with open(os.path.join(destination_directory, f"{folder}_{today}.txt"), 'w') as f:
        f.write(content)

print("Concatenation completed.")
