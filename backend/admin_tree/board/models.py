from django.db import models


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=10)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'posts'


class Reply(models.Model):
    content = models.CharField(max_length=120)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'replies'
