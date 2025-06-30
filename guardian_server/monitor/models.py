from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta


class DeviceData(models.Model):
    device_id = models.CharField(max_length=100)
    heart_rate = models.IntegerField()
    temperature = models.FloatField()
    bp_systolic = models.IntegerField()
    bp_diastolic = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now)

    def is_online(self):
        """Device is online if data was received within the last 2 minutes."""
        return timezone.now() - self.last_seen <= timedelta(minutes=2)

    def __str__(self):
        return f"{self.device_id} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class SensorHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heart_rate = models.IntegerField()
    temperature = models.FloatField()
    bp_systolic = models.IntegerField()
    bp_diastolic = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class Notification(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    heart_rate = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    bp_systolic = models.IntegerField(null=True, blank=True)
    bp_diastolic = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.message}"
