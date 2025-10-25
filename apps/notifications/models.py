from django.db import models


class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        # Shorten long messages for admin readability
        return (self.message[:75] + "...") if len(self.message) > 78 else self.message
