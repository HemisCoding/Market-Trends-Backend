from django.db import models


# Create your models here.

class SentimentScore(models.Model):
    id = models.BigAutoField(primary_key=True)
    text = models.TextField(verbose_name="Text")
    score = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Sentiment Score")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")