#!/usr/bin/env python3
"""
Example usage of the Ultimate Crawler with multiple accounts
"""

from ultimate_crawler import MultiAccountCrawler, Account, CrawlerConfig

def main():
    """Example of how to use the crawler with multiple accounts"""
    
    # Define your accounts here
    accounts = [
        Account("username1", "password1"),
        Account("username2", "password2"),
        Account("username3", "password3"),
        # Add more accounts as needed
    ]
    
    # Optional: Customize configuration
    config = CrawlerConfig(
        TOTAL_QUESTIONS=50,  # Change total questions needed
        MIN_DELAY_SHORT=3.0,  # Minimum short delay
        MAX_DELAY_SHORT=8.0,  # Maximum short delay
        MIN_DELAY_LONG=12.0,  # Minimum long delay
        MAX_DELAY_LONG=20.0,  # Maximum long delay
        ACCOUNT_SWITCH_DELAY=45.0,  # Delay between account switches
        QUIZ_DATA_FILE='my_quiz_data.json'  # Custom output file
    )
    
    # Create and run crawler
    crawler = MultiAccountCrawler(accounts, config)
    crawler.run()

if __name__ == "__main__":
    main()
