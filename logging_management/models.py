from django.db import models


class Log(models.Model):
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=100)
    method = models.CharField(max_length=10, null=True, blank=True)
    payload = models.TextField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    action_started_at = models.DateTimeField(auto_now_add=True)
    action_completed_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} -> {self.action}"
