# Set environment PROJECT = "ORT"
# sudo docker run -d --restart always -v $(pwd)/data:/app/data -t stream_recorder

# export PROJECT="ORT"
sudo docker run -d --restart always -v $(pwd)/data:/app/data -e PROJECT="ORT" -t stream_recorder