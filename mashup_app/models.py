from django.db import models

class Mashup(models.Model):
    singer_name = models.CharField(max_length=100)
    number_of_videos = models.IntegerField()
    duration = models.IntegerField()
    email = models.EmailField()
