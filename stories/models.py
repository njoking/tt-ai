from django.db import models

# Create your models here.
from django.db import models

class Story(models.Model):
    story_text = models.TextField()
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    image_file = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
