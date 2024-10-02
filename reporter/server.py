import os
import logging
import requests
import time
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_files(directory, BASE_URL, headers):
    """Lists files in the specified directory."""
    response = requests.get(f"{BASE_URL}/list-files/{directory}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        # print(f"Error: {response.status_code}, {response.text}")
        logger.error(f"Error: {response.status_code}, {response.text}")
        return []
    
def test():
    # Init with current datetime
    report_text = f"Chronocast status at {datetime.datetime.now()}\n"
    projects = [
        {"name": "belarusone", "BASE_URL": "http://34.118.89.125:8054"},
        {"name": "oneplusone", "BASE_URL": "http://34.118.89.125:8054"},
        {"name": "ORT", "BASE_URL": "http://45.132.17.180:8054"},
        {"name": "russiaone", "BASE_URL": "http://45.132.17.180:8054"},
    ]
    API_TOKEN = os.environ.get("API_TOKEN", "")
    if not API_TOKEN:
        logger.error('Please set the API_TOKEN environment variable. "export API_TOKEN=your_token_here"')
        return
    headers = {"Authorization": API_TOKEN}
    for project in projects:
        project_name = project['name']
        BASE_URL = project['BASE_URL']
        path = f'data/audio/{project_name}'
        files = list_files(path, BASE_URL, headers)
        # logger.info(f"Found {len(files)} files in {path}")
        report_text += f"{len(files)} files in {path}\n"
    logger.info(f"Sending report: {report_text}")

    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    telegram_group_id = os.environ.get("TELEGRAM_GROUP_ID", "")
    if not telegram_bot_token:
        logger.error('Please set the TELEGRAM_BOT_TOKEN environment variable.')
        return
    if not telegram_group_id:
        logger.error('Please set the TELEGRAM_GROUP_ID environment variable.')
        return
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {
        "chat_id": telegram_group_id,
        "text": report_text
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending report via telegram: {e}")

def main():
    while True:
        test()
        # Sleep for 24 hours
        time.sleep(24 * 60 * 60)

if __name__ == '__main__':
    main()
