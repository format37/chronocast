# sudo docker-compose up --build --d --force-recreate
# Build
docker build -t bq-export-service .

# Run with mounted credentials
docker run -v ./credentials_full.json:/app/credentials.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  bq-export-service