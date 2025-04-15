import os
from ai_news_poster import AINewsPoster
import schedule
import time
from datetime import datetime
import signal
import sys

def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

def run_scheduler():
    poster = AINewsPoster()
    
    # Schedule the job to run daily at 9:00 AM UTC
    schedule.every().day.at("09:00").do(poster.run)
    
    print(f"\nScheduler started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("Will post daily at 9:00 AM UTC")
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            print(f"Error in scheduler loop: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    run_scheduler() 