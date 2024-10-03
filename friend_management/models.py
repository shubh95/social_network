from django.db import models


class FriendRequest(models.Model):
    from_user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="to_user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, default="pending", choices=[("pending", "pending"), ("accepted", "accepted"), ("rejected", "rejected"), ("unsent", "unsent")])

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"



class Friend(models.Model):
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="user")
    friend = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="friend")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} -> {self.friend}"
    