from django.db import models


# Create your models here.
class Logs(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    model = models.CharField(max_length=100, null=False, blank=False)
    id_register = models.CharField(max_length=255, null=False, blank=False)
    json_data = models.JSONField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'
