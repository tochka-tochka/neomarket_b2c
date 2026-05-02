from uuid import uuid4

from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField()
    slug = models.CharField()
    description = models.CharField(null=True, blank=True)
    image_url = models.CharField(null=True, blank=True)
    parent_id = models.UUIDField(null=True, blank=True)
    seo_title = models.CharField(null=True, blank=True)
    seo_description = models.CharField(null=True, blank=True)


class CategorySEOKeyword(models.Model):
    category_id = models.UUIDField()
    name = models.CharField()


class CategoryFilter(models.Model):
    category_id = models.UUIDField()
    slug = models.CharField()
    name = models.CharField()
    type = models.CharField()
    values = models.JSONField()
