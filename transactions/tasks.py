# tasks.py
from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_variations_task():
    logger.info('Starting generate_variations_task')
    try:
        call_command('generate_variations')
        logger.info('generate_variations_task completed successfully')
    except Exception as e:
        logger.error(f'Error in generate_variations_task: {e}')
