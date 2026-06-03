from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'users'
        app_label = 'src'

    def __str__(self):
        return self.username
