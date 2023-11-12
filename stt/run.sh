# sudo docker run --gpus '"device=0"' -p 2700:2700 -t whisper
# Create folder ./cache if not exist
mkdir -p cache
# Create folder ./data/transcriptions if not exist
# mkdir -p /home/alex/projects/stream_recorder/data/transcriptions
# Create folder ./data/processed if not exist
# mkdir -p /home/alex/projects/stream_recorder/data/processed
# sudo docker run --gpus '"device=0"' -p 2700:2700 -v $(pwd)/cache:/app/cache -t whisper_official
# -d --restart always 
sudo docker stop stt
sudo docker rm stt
sudo docker run \
    -d \
    --restart always \
    --gpus '"device=0"' \
    -v $(pwd)/cache:/app/cache \
    -v /home/alex/projects/chronocast/data:/app/data \
    -e BASE_URL=http://www.j1f.ru:8054 \
    -e API_TOKEN=8VsdROHbUVeGKM3GsqB9UMGL1QvrXWquruTs9zImj8FgDC0AuWL4c70R4y7IhP6f7AYJXA \
    -e PROJECT=ORT \
    --name stt \
    -t stt
