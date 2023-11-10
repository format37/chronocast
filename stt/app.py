import whisper
import os
import time
import pandas as pd
import logging

# Init logging with level INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    model_name = "large"
    logger.info(f"Loading the model {model_name}...")
    model = whisper.load_model(model_name, download_root='/app/cache')

    while(True):
        # get list of files in /app/data/audio sorted ascending
        files = os.listdir("/app/data/audio")
        files.sort()
        logger.info(f"Found {len(files)} files in /app/data/audio")

        iterator = 0

        # iterate files
        for file in files:
            # get file name
            filename = os.path.basename(file)
            # get file path
            filepath = os.path.join("/app/data/audio", file)
            logger.info(f"Processing file {filename}...")
            result = model.transcribe(
                filepath,
                language="ru",
                temperature=0.8,
                prompt="Аудиозапись с телевизора"
            )
            # print(result["text"])

            # transcription = filename
            transcription = result["text"]
            logger.info(f"Transcription length: {len(transcription)}")
            # save transcription to file
            transcription_filename = filename.replace(".mp3", ".txt")
            with open(f"/app/data/transcriptions/{transcription_filename}", "w") as f:
                f.write(transcription)

            # move file to /app/data/processed
            os.rename(filepath, f"/app/data/processed/{filename}")

            iterator += 1
            # break before the last file
            if iterator >= len(files)-1:
            # if iterator >= 2:
                break

        # wait for 600 seconds
        print("Queue is empty. Waiting for 10 minutes...")
        time.sleep(600)


if __name__ == "__main__":
    main()
