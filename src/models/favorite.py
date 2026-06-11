from django.db import models
import uuid


class Favorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    product_id = models.UUIDField(db_index=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'product_id'],
                name='unique_user_product'
            )
        ]
