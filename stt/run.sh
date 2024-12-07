# Create folder ./cache if not exist
mkdir -p cache
sudo docker stop stt
sudo docker rm stt
sudo docker run \
    --gpus '"device=0"' \
    --restart always \
    --name stt \
    -d \
    -v $(pwd)/cache:/app/cache \
    -v /home/alex/projects/chronocast/data:/app/data \
    -v $(pwd)/config_my.json:/app/config.json \
    -v $(pwd)/credentials_full.json:/app/credentials_full.json \
    -v ~/.config/gcloud:/root/.config/gcloud:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials_full.json \
    -t stt
