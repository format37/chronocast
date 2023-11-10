import subprocess
import shlex
import time
import os
import logging

# Define the logging configuration as info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def record_stream(segment_duration=600):  # segment_duration is in seconds (10 minutes)
    logger.info("Recording started.")
    # Define the command to get the stream URL
    streamlink_cmd = "streamlink https://www.1tv.ru/live best -O"

    project = os.environ.get('PROJECT')
    os.makedirs(f"data/audio/{project}", exist_ok=True)
    
    # Define the FFmpeg command to extract audio and split it into segments
    # ffmpeg_cmd = ("ffmpeg -i pipe:0 -f segment -segment_time {duration} "
    #               "-c copy -vn -strftime 1 'output_%Y-%m-%d_%H-%M-%S.mp3'").format(duration=segment_duration)
    ffmpeg_cmd = ("ffmpeg -i pipe:0 -f segment -segment_time {duration} "
              "-vn -ar 44100 -ac 2 -b:a 192k -strftime 1 'data/audio/{project}/%Y-%m-%d_%H-%M-%S.mp3'").format(duration=segment_duration, project=project)

    logger.info("Running streamlink command: %s", ffmpeg_cmd)

    # Start the Streamlink process
    streamlink_process = subprocess.Popen(shlex.split(streamlink_cmd), stdout=subprocess.PIPE)
    
    # Start the FFmpeg process
    ffmpeg_process = subprocess.Popen(shlex.split(ffmpeg_cmd), stdin=streamlink_process.stdout)
    
    try:
        # Wait for the FFmpeg process to finish (it won't if it's a 24/7 stream)
        ffmpeg_process.wait()
    except KeyboardInterrupt:
        # Handle the interrupt signal to gracefully shutdown the processes
        streamlink_process.terminate()
        ffmpeg_process.terminate()
        
    print("Recording stopped.")

# Run the recording function
if __name__ == "__main__":
    record_stream()
