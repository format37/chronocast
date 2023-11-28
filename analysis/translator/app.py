from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import logging
import os
import torch

# Init logging with level INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def model_is_cached():
    """ Check if huggingface directory exist in cache directory """
    cache_dir = '/root/.cache/'
    if os.path.isdir(cache_dir):
        if os.path.isdir(os.path.join(cache_dir, 'huggingface')):
            return True
    return False



def main():

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Using device: {}".format(device))

    logger.info("Loading and caching model and tokenizer...")
    model_name = "facebook/mbart-large-50-many-to-one-mmt"    
    model = MBartForConditionalGeneration.from_pretrained(model_name).to(device)
    tokenizer = MBart50TokenizerFast.from_pretrained(model_name)

    """
    article_hi = "संयुक्त राष्ट्र के प्रमुख का कहना है कि सीरिया में कोई सैन्य समाधान नहीं है"
    article_ar = "الأمين العام للأمم المتحدة يقول إنه لا يوجد حل عسكري في سوريا."

    # translate Hindi to English
    logger.info("Translating Hindi to English...")
    tokenizer.src_lang = "hi_IN"
    encoded_hi = tokenizer(article_hi, return_tensors="pt").to(device)
    generated_tokens = model.generate(**encoded_hi)
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    logger.info(translated_text)
    # => "The head of the UN says there is no military solution in Syria."

    # translate Arabic to English
    logger.info("Translating Arabic to English...")
    tokenizer.src_lang = "ar_AR"
    encoded_ar = tokenizer(article_ar, return_tensors="pt").to(device)
    generated_tokens = model.generate(**encoded_ar)
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    logger.info(translated_text)
    # => "The Secretary-General of the United Nations says there is no military solution in Syria."
    """

    # Read all files in './data/' directory
    data_dir = './data/concatenated/'
    logger.info(f"Reading all files in {data_dir} directory...")
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            logger.info("Reading file: {}".format(filename))
            with open(os.path.join(data_dir, filename), 'r') as f:
                text = f.read()
                logger.info("Translating text...")
                encoded_hi = tokenizer(text, return_tensors="pt").to(device)
                generated_tokens = model.generate(**encoded_hi)
                translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
                logger.info(translated_text)
                logger.info("Writing translated text to file...")
                with open(os.path.join(data_dir, filename + '.translated.txt'), 'w') as f:
                    f.write(translated_text[0])
                logger.info(f"{filename} done.")
        else:
            continue
    
    logger.info("Done!")

if __name__ == "__main__":
    main()
