"""
Background Jobs Scheduler — Orchestrate all data collectors.
Uses APScheduler to run collectors on schedules:
  - Website monitoring: Daily at 2am UTC
  - RSS feeds: Every 6 hours
  - Product Hunt: Daily at 9am UTC
  - Job board: Bi-weekly (Tuesday at 10am UTC)
  - News monitoring: Daily at 12pm UTC
"""

import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging

# Import all data collectors
from data_collectors import website_monitor
from data_collectors import rss_parser
from data_collectors import product_hunt
from data_collectors import job_board
from data_collectors import news_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_website_monitor():
    """Run website monitoring collector."""
    try:
        logger.info("Starting website monitor...")
        result = website_monitor.monitor_competitor_websites()
        logger.info(f"Website monitor completed: {result}")
    except Exception as e:
        logger.error(f"Website monitor failed: {e}")


def run_rss_parser():
    """Run RSS feed parser collector."""
    try:
        logger.info("Starting RSS parser...")
        result = rss_parser.monitor_rss_feeds()
        logger.info(f"RSS parser completed: {result}")
    except Exception as e:
        logger.error(f"RSS parser failed: {e}")


def run_product_hunt():
    """Run Product Hunt collector."""
    try:
        logger.info("Starting Product Hunt monitor...")
        result = product_hunt.monitor_product_hunt()
        logger.info(f"Product Hunt monitor completed: {result}")
    except Exception as e:
        logger.error(f"Product Hunt monitor failed: {e}")


def run_job_board():
    """Run job board collector."""
    try:
        logger.info("Starting job board monitor...")
        result = job_board.monitor_job_boards()
        logger.info(f"Job board monitor completed: {result}")
    except Exception as e:
        logger.error(f"Job board monitor failed: {e}")


def run_news_monitor():
    """Run news monitoring collector."""
    try:
        logger.info("Starting news monitor...")
        api_key = os.getenv("NEWSAPI_KEY")
        result = news_monitor.monitor_news(api_key)
        logger.info(f"News monitor completed: {result}")
    except Exception as e:
        logger.error(f"News monitor failed: {e}")


def start_scheduler():
    """
    Start background scheduler with all collectors.
    Returns: scheduler instance (useful for testing/cleanup).
    """
    scheduler = BackgroundScheduler()

    # Website monitoring: Daily at 2am UTC
    scheduler.add_job(
        run_website_monitor,
        trigger=CronTrigger(hour=2, minute=0, timezone='UTC'),
        id='website_monitor',
        name='Website Monitor (Daily 2am UTC)',
        replace_existing=True
    )

    # RSS feeds: Every 6 hours
    scheduler.add_job(
        run_rss_parser,
        trigger=IntervalTrigger(hours=6),
        id='rss_parser',
        name='RSS Parser (Every 6 hours)',
        replace_existing=True
    )

    # Product Hunt: Daily at 9am UTC
    scheduler.add_job(
        run_product_hunt,
        trigger=CronTrigger(hour=9, minute=0, timezone='UTC'),
        id='product_hunt',
        name='Product Hunt Monitor (Daily 9am UTC)',
        replace_existing=True
    )

    # Job board: Bi-weekly on Tuesday at 10am UTC
    scheduler.add_job(
        run_job_board,
        trigger=CronTrigger(day_of_week=1, hour=10, minute=0, timezone='UTC'),
        id='job_board',
        name='Job Board Monitor (Tuesday 10am UTC)',
        replace_existing=True
    )

    # News monitoring: Daily at 12pm UTC
    scheduler.add_job(
        run_news_monitor,
        trigger=CronTrigger(hour=12, minute=0, timezone='UTC'),
        id='news_monitor',
        name='News Monitor (Daily 12pm UTC)',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started with 5 collection jobs")
    return scheduler


def trigger_manual_collection(collector_name: str):
    """
    Manually trigger a single collector.
    Useful for testing and on-demand updates.

    Args:
        collector_name: One of 'website', 'rss', 'jobs', 'news', 'product_hunt'
    """
    collectors = {
        'website': run_website_monitor,
        'rss': run_rss_parser,
        'jobs': run_job_board,
        'news': run_news_monitor,
        'product_hunt': run_product_hunt
    }

    if collector_name not in collectors:
        logger.error(f"Unknown collector: {collector_name}")
        return

    logger.info(f"Manually triggering {collector_name} collector...")
    try:
        collectors[collector_name]()
        logger.info(f"{collector_name} collector completed successfully")
    except Exception as e:
        logger.error(f"{collector_name} collector failed: {e}")


def trigger_all_collectors():
    """
    Manually trigger all collectors at once.
    Useful for initial setup or full refresh.
    """
    logger.info("Triggering all collectors...")
    run_website_monitor()
    run_rss_parser()
    run_product_hunt()
    run_job_board()
    run_news_monitor()
    logger.info("All collectors completed")


if __name__ == "__main__":
    # Start scheduler and run indefinitely
    scheduler = start_scheduler()
    try:
        scheduler.start()
        logger.info("Scheduler is running. Press Ctrl+C to exit.")
        # Keep the scheduler running
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
