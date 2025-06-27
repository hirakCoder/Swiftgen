#!/usr/bin/env python3
"""
Batch Swift Code Scraper - Runs scraping in controlled batches
"""

import asyncio
import logging
from swift_code_scraper import SwiftCodeScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_batch_scraping():
    """Run scraping in smaller batches to avoid timeouts"""
    scraper = SwiftCodeScraper()
    
    # Reduced queries for initial testing
    queries = [
        ("SwiftUI app", 20),
        ("iOS app Swift", 20),
        ("SwiftUI MVVM", 10)
    ]
    
    total_scraped = 0
    
    for query, max_repos in queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting batch: '{query}' (max {max_repos} repos)")
        logger.info(f"{'='*60}")
        
        try:
            await scraper.scrape_github_repos(query, max_repos=max_repos)
            total_scraped += max_repos
            
            # Create intermediate dataset after each batch
            logger.info(f"Creating training dataset after batch...")
            scraper.create_training_dataset()
            
            # Longer pause between queries to respect rate limits
            logger.info(f"Pausing 10 seconds before next batch...")
            await asyncio.sleep(10)
            
        except Exception as e:
            logger.error(f"Error in batch '{query}': {e}")
            continue
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Scraping complete! Total attempted: {total_scraped} repos")
    logger.info(f"Check swift_training_data/ for collected data")
    logger.info(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(run_batch_scraping())