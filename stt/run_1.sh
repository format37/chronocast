# Create folder ./cache if not exist
mkdir -p cache
sudo docker stop stt_1
sudo docker rm stt_1
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
    -t stt
