# Create folder ./cache if not exist
mkdir -p cache
sudo docker stop stt_0
sudo docker rm stt_0
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
