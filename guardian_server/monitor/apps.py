from django.apps import AppConfig
import threading
import time
from django.utils import timezone
from datetime import timedelta


def save_history_job():
    import django

    django.setup()
    from django.contrib.auth import get_user_model
    from .models import DeviceData, SensorHistory

    User = get_user_model()

    while True:
        try:
            # Get the latest device data
            latest = DeviceData.objects.latest("timestamp")
        except DeviceData.DoesNotExist:
            print("No DeviceData available yet.")
            latest = None

        if latest and latest.is_online():
            # Check if a SensorHistory record was created in last 3 minutes for this device/user combo
            # We assume one SensorHistory per user, but same data used for all users here
            three_minutes_ago = timezone.now() - timedelta(minutes=3)

            recent_record = SensorHistory.objects.filter(
                timestamp__gte=three_minutes_ago
            ).exists()

            if not recent_record:
                print(f"[{timezone.now()}] Device online - recording sensor data.")

                for user in User.objects.all():
                    SensorHistory.objects.create(
                        user=user,
                        heart_rate=latest.heart_rate,
                        temperature=latest.temperature,
                        bp_systolic=latest.bp_systolic,
                        bp_diastolic=latest.bp_diastolic,
                        latitude=latest.latitude,
                        longitude=latest.longitude,
                        timestamp=timezone.now(),
                    )
            else:
                print(
                    f"[{timezone.now()}] Record already created in last 3 minutes. Skipping."
                )

        else:
            print(
                f"[{timezone.now()}] Device offline or no data available. No record created."
            )

        # Wait 3 minutes before next check
        time.sleep(180)


class MonitorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitor"

    def ready(self):
        threading.Thread(target=save_history_job, daemon=True).start()
