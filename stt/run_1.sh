# Create folder ./cache if not exist
mkdir -p cache

# Check if the container exists, then stop and remove it
if [ $(sudo docker ps -a -f name=stt_1 --format '{{.Names}}') = 'stt_1' ]; then
    sudo docker stop stt_1
    sudo docker rm stt_1
fi

# Run the Docker container
sudo docker run \
    --gpus '"device=1"' \
    --restart always \
    --name stt_1 \
    -d \
    -v $(pwd)/cache:/app/cache \
    -v /home/alex/projects/chronocast/data:/app/data \
    -v $(pwd)/config_1.json:/app/config.json \
    -v $(pwd)/credentials_full.json:/app/credentials_full.json \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials_full.json \
    -e CUDA_LAUNCH_BLOCKING=1 \
    -t stt
