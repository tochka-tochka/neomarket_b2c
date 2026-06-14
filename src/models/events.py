from django.db import models


class ProcessedEvent(models.Model):
    idempotency_key = models.UUIDField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processed_events'
