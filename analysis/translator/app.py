from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import logging
import os
import torch
import re
import time
import datetime

# Init logging with level INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_into_batches(text, batch_size):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [' '.join(sentences[i:i+batch_size]) for i in range(0, len(sentences), batch_size)]

def translate_batch(text, model, tokenizer, device):
    encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to(device)
    generated_tokens = model.generate(**encoded)
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

def main():
    start_time = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Using device: {}".format(device))

    logger.info("Loading and caching model and tokenizer...")
    model_name = "facebook/mbart-large-50-many-to-one-mmt"    
    model = MBartForConditionalGeneration.from_pretrained(model_name).to(device)
    tokenizer = MBart50TokenizerFast.from_pretrained(model_name)

    data_dir = './data/concatenated/'
    destination_dir = './data/translated/'
    os.makedirs(destination_dir, exist_ok=True)
    batch_size = 200  # Define the number of sentences per batch

    logger.info(f"Reading all files in {data_dir} directory...")
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(data_dir, filename)
            logger.info(f"Reading file: {file_path}")

            with open(file_path, 'r') as file:
                text = file.read()
                batches = split_into_batches(text, batch_size)
                translated_text = []

                batches_count = len(batches)
                batch_id = 0

                for batch in batches:
                    logger.info(f"{filename} Translating text batch: {batch_id} of {batches_count}")
                    translation = translate_batch(batch, model, tokenizer, device)
                    translated_text.extend(translation)
                    batch_id += 1

                translated_text_str = ' '.join(translated_text)
                logger.info("Writing translated text to file...")

                translated_file_path = os.path.join(destination_dir, filename)
                with open(translated_file_path, 'w') as translated_file:
                    translated_file.write(translated_text_str)

                logger.info(f"{filename} done.")
        else:
            continue

    end_time = time.time()

    logger.info("Done!")

    logger.info(f"Execution time: {datetime.timedelta(seconds=end_time - start_time)}")
    # Human readable format
    logger.info(f"Execution time: {time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))}")


if __name__ == "__main__":
    main()
