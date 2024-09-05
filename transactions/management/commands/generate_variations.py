import os
import django
import uuid
import logging
from django.core.management.base import BaseCommand
from transactions.models import SanctionRecord, NameVariation
from transactions.name_variations import generate_name_variations  # Import from name_variation.py

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

def create_variations_for_record(record):
    """
    Generate and save variations for a given sanction record.
    """
    try:
        # Fetch the sanction record by id_original
        sanction_record = SanctionRecord.objects.get(id_original=record['ID Original'])
        name = f"{record.get('First Name', '')} {record.get('Last Name', '')}".strip()

        # Generate variations for the name using different algorithms
        variations = generate_name_variations(name)

        if not variations:
            logger.info(f"No variations generated for record with ID Original: {record['ID Original']}")
            return

        variation_objects = []
        for variation, score in variations.items():
            if not NameVariation.objects.filter(sanction_record_id=sanction_record.id, variation=variation).exists():
                variation_objects.append(
                    NameVariation(
                        sanction_record_id=sanction_record.id,
                        variation=variation,
                        score=score,
                        variation_id=str(uuid.uuid4())
                    )
                )

        # Bulk create all variations for the current record
        if variation_objects:
            NameVariation.objects.bulk_create(variation_objects)
            logger.info(f"Created {len(variation_objects)} variations for SanctionRecord ID Original: {record['ID Original']}")
        else:
            logger.info(f"No new variations created for SanctionRecord ID Original: {record['ID Original']}")

    except SanctionRecord.DoesNotExist:
        logger.error(f"SanctionRecord not found for ID Original: {record['ID Original']}")
    except Exception as e:
        logger.error(f"Error generating variations for record {record}: {e}")

class Command(BaseCommand):
    help = 'Generate name variations for the first 10 sanction records and display variation count'

    def handle(self, *args, **options):
        logger.info("Starting to generate name variations...")

        # Fetch the first 10 records
        all_records = SanctionRecord.objects.all()[:1000]
        logger.info(f"Processing the first {all_records.count()} records out of {SanctionRecord.objects.count()} total records.")

        for record in all_records:
            # Generate variations for the record
            create_variations_for_record({
                'ID Original': record.id_original,
                'First Name': record.first_name,
                'Last Name': record.last_name,
            })

            # Fetch and display the updated variation count for the record
            variation_count = NameVariation.objects.filter(sanction_record_id=record.id).count()
            print(f"ID Original: {record.id_original}, Variation Count: {variation_count}")

        self.stdout.write(self.style.SUCCESS('Successfully generated name variations '))
        logger.info("Completed generating name variations.")
