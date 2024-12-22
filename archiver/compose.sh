# Build
docker build -t bq-export-service .

# Run with mounted credentials as a daemon
docker run -d -v ./credentials_full.json:/app/credentials.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  bq-export-service