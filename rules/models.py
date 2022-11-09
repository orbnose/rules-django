from django.db import models

class Rule(models.Model):
    name = models.CharField(max_length = 200)
    logic_string = models.CharField(max_length = 200)
    json_logic = models.JSONField()