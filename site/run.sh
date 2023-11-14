sudo docker stop site
sudo docker rm site
#   --restart always \  
#   -d \
sudo docker run \
    --gpus '"device=0"' \
    --name site \
    -v $(pwd)/cache:/app/cache \
    -v /home/alex/projects/chronocast/data:/app/data \
    -v $(pwd)/config.json:/app/config.json \
    -v $(pwd)/credentials_full.json:/app/credentials_full.json \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials_full.json \
    -t site
