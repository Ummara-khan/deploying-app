from django.db import models
import uuid
from django.utils.text import slugify
import random

class SanctionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    list_name = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    id_original = models.CharField(max_length=255, blank=True, null=True)
    entity_type = models.CharField(max_length=255, blank=True, null=True)
    identity_numbers = models.CharField(max_length=255, blank=True, null=True)
    identity_types = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    watchlist_country = models.CharField(max_length=255, blank=True, null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)
    alias_type = models.CharField(max_length=255, blank=True, null=True)
    watch_list_id = models.UUIDField(default=uuid.uuid4, editable=False)
    dataset_id = models.UUIDField(default=uuid.uuid4, editable=False)
    no_of_variations = models.IntegerField(default=0)
  
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.id_original})"

    class Meta:
        indexes = [
            models.Index(fields=['id_original']),
            models.Index(fields=['dataset_id']),
            models.Index(fields=['watch_list_id']),
        ]

class UploadStatistics(models.Model):
    list_name = models.CharField(max_length=255)
    last_import_date = models.DateField()
    records_added = models.IntegerField()
    records_updated = models.IntegerField()
    records_deleted = models.IntegerField()
    total_active_records = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    processed = models.BooleanField(default=False)
    file_hash = models.CharField(max_length=64, unique=True)  # Add this field
    
    def __str__(self):
        return f"Statistics for {self.list_name} on {self.last_import_date}"

from django.db import models

class NameVariation(models.Model):
    sanction_record = models.ForeignKey(SanctionRecord, on_delete=models.CASCADE, related_name='variations')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    sanc_id = models.CharField(max_length=255) 
    algorithm = models.CharField(max_length=255) 
    no_of_variations = models.IntegerField(default=0)
    variation = models.CharField(max_length=255, null=True, blank=True) 
    variation_id = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    test_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.variation_id} (Score: {self.score})"

    class Meta:
        indexes = [
            models.Index(fields=['sanc_id']),
            models.Index(fields=['variation_id']),
        ]

# transactions/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()




class SanctionRecordDetail(models.Model):
    sanction_record = models.ForeignKey(SanctionRecord, on_delete=models.CASCADE)
    name = models.CharField(max_length=510)  # Combine first name and last name
    entity_type = models.CharField(max_length=50)
    list_name = models.CharField(max_length=255)
    variations = models.ManyToManyField(NameVariation)  # Many-to-many relationship to handle multiple variations
    score = models.IntegerField(default=0)  # Aggregate or set based on variations


  

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction by {self.user.email} on {self.timestamp}'



class ProcessedFile(models.Model):
    file_name = models.CharField(max_length=255, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    list_name = models.CharField(max_length=50)
