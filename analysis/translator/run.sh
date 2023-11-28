# Create folder ./cache if not exist
mkdir -p cache

# Run the Docker container
sudo docker run \
    --gpus '"device=0"' \
    --rm \
    --name translator \
    -v $(pwd)/cache:/root/.cache \
    -v /home/alex/projects/chronocast/analysis/data:/app/data \
    -t translator
