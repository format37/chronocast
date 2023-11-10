from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
import os
from fastapi import Request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_api_token(request: Request):
    expected_token = os.getenv("API_TOKEN")
    provided_token = request.headers.get("Authorization")

    if provided_token != expected_token:
        logger.error("Invalid API token provided:")
        logger.info(f"Expected: {expected_token}")
        logger.info(f"Provided: {provided_token}")
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/list-files/{path:path}")
async def list_files(path: str, token: str = Depends(get_api_token)):
    """Endpoint to list files in the specified directory."""
    full_path = os.path.join('.', path)
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        raise HTTPException(status_code=404, detail="Directory not found")

    files = sorted(os.listdir(full_path))
    return files

@app.get("/download-file/{path:path}")
async def download_file(path: str, token: str = Depends(get_api_token)):
    """Endpoint to download a file."""
    if not os.path.exists(path) or os.path.isdir(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path)

@app.delete("/delete-file/{path:path}")
async def delete_file(path: str, token: str = Depends(get_api_token)):
    """Endpoint to delete a file."""
    if not os.path.exists(path) or os.path.isdir(path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(path)
    return {"detail": "File deleted"}

# Run the server with: uvicorn filename:app --reload
