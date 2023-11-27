# Create folder ./cache if not exist
mkdir -p cache

# Check if the container exists, then stop and remove it
if [ $(sudo docker ps -a -f name=stt_0 --format '{{.Names}}') = 'stt_0' ]; then
    sudo docker stop stt_0
    sudo docker rm stt_0
fi

# Run the Docker container
sudo docker run \
    --gpus '"device=0"' \
    --restart always \
    --name stt_0 \
    -d \
    -v $(pwd)/cache:/app/cache \
    -v /home/alex/projects/chronocast/data:/app/data \
    -v $(pwd)/config_0.json:/app/config.json \
    -v $(pwd)/credentials_full.json:/app/credentials_full.json \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials_full.json \
    -t stt
