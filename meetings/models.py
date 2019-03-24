from django.db import models

# Create your models here.

class Meeting(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    sinceWhen = models.DateTimeField()
    tilWhen = models.DateTimeField()
    user = models.ForeignKey('auth.User', related_name='meetings', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', 'sinceWhen', 'tilWhen', 'user')