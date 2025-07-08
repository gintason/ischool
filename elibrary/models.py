from django.db import models

# Create your models here.
class ELibraryChapter(models.Model):
    title = models.CharField(max_length=255)
    content_link = models.URLField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title