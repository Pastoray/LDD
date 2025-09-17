import asyncio
import sys
import os
import logging
from dotenv import load_dotenv
from scraper import Scraper
from problem_uploader import LinkedInUploader
from utils.notifier import Notifier
from ai_models.llm import ContentGenerator

load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

log_file_path = os.path.join(script_dir, "error.log")
logging.basicConfig(
    filename = log_file_path,
    level = logging.ERROR,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

async def manage_workflow(llm_model_name: str,):
    print("Starting the main workflow...")
    print("Scraping problem...")

    try:
        scraper = Scraper()
        scraped_data = await scraper.scrape_daily_challenge()

    except Exception as e:
        error_message = f"Failed to scrape data.\nError: {e}\nExiting..."
        logging.error(error_message)
        print(error_message)
        sys.exit(1)

    print("Scraping succeeded")
    print("Generating explanation...")
    
    try:
        content_gen = ContentGenerator(llm_model_name)
        explanation = content_gen.generate_post(**scraped_data)

    except Exception as e:
        error_message = f"Failed to explain problem solution.\nError: {e}\nExiting..."
        logging.error(error_message)
        print(error_message)
        sys.exit(1)

    print("\n" + "=" * 50)
    print("AI-Generated explanation")
    print("=" * 50)
    print(explanation)

    print("Publishing solution...")

    try:
        LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
        LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
        
        platform = "telegram"
        TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
        TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

        notifier = Notifier(platform, TELEGRAM_API_KEY, TELEGRAM_CHAT_ID)

        uploader = LinkedInUploader(LINKEDIN_EMAIL, LINKEDIN_PASSWORD, notifier)
        await uploader.upload(explanation)

    except Exception as e:
        error_message = f"Failed to upload solution.\nError: {e}\nExiting..."
        logging.error(error_message)
        print(error_message)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <llm_model_name>")
        sys.exit(1)

    llm_model_name = sys.argv[1]
    asyncio.run(manage_workflow(llm_model_name))

if __name__ == "__main__":
    main()
