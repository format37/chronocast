#!/bin/bash
mkdir -p ./data
# -e TRANSFORMERS_CACHE=/custom_cache \
# --network host \
sudo docker run \
    -it \
    --gpus device=0 \
    --rm \
    --name embeddings \
    -v $(pwd)/app.py:/app/app.py \
    -v $(pwd)/cache:/root/.cache \
    -v /home/alex/projects/chronocast/analysis/data:/app/data \
    embeddings
