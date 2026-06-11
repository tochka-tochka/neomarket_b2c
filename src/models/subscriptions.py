from django.db import models
import uuid


class ProductSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    product_id = models.UUIDField(db_index=True)
    events = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'product_id'],
                name='unique_user_product_subscription'
            )
        ]
        