sudo docker stop file_server
sudo docker rm file_server
# -d \
# --restart always \
sudo docker run \
    --network="host" \
    --name file_server \
    -v $(pwd)/data:/server/data \
    -e API_TOKEN=your_secret_token \
    file_server