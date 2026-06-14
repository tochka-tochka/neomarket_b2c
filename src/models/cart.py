from django.db import models
import uuid


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    session_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    sku_id = models.UUIDField(db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unavailable_reason = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cart_items'
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'sku_id'],
                condition=models.Q(user_id__isnull=False),
                name='unique_user_sku'
            ),
            models.UniqueConstraint(
                fields=['session_id', 'sku_id'],
                condition=models.Q(session_id__isnull=False),
                name='unique_session_sku'
            ),
            models.CheckConstraint(
                condition=(
                        models.Q(user_id__isnull=False) |
                        models.Q(session_id__isnull=False)
                ),
                name='cart_identity_required'
            )
        ]