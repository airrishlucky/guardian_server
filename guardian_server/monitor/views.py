from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import logout
from datetime import timedelta
from .models import Notification
from django.db.models import Q
from .serializers import DeviceDataSerializer
from .models import DeviceData, SensorHistory


# === API: Receive Sensor Data ===
@api_view(["POST"])
def receive_data(request):
    serializer = DeviceDataSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save(last_seen=timezone.now())

        # Check last history entry
        latest_history = SensorHistory.objects.order_by("-timestamp").first()

        should_record = False
        if instance.is_online():
            if latest_history is None:
                should_record = True
            else:
                time_diff = timezone.now() - latest_history.timestamp
                if time_diff >= timedelta(minutes=5):
                    should_record = True

        if should_record:
            SensorHistory.objects.create(
                heart_rate=instance.heart_rate,
                temperature=instance.temperature,
                bp_systolic=instance.bp_systolic,
                bp_diastolic=instance.bp_diastolic,
                latitude=instance.latitude,
                longitude=instance.longitude,
            )

        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# === API: Get Latest Device Data ===
@api_view(["GET"])
def api_latest_data(request):
    try:
        latest = DeviceData.objects.latest("last_seen")
        return Response(
            {
                "heart_rate": latest.heart_rate,
                "temperature": latest.temperature,
                "bp_systolic": latest.bp_systolic,
                "bp_diastolic": latest.bp_diastolic,
                "latitude": latest.latitude,
                "longitude": latest.longitude,
                "timestamp": latest.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "is_online": latest.is_online(),
            }
        )
    except DeviceData.DoesNotExist:
        return Response(
            {"error": "No data available"}, status=status.HTTP_404_NOT_FOUND
        )


# === Auth: Register ===
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


# === Auth: Logout ===
def logout_view(request):
    logout(request)
    return redirect("login")


# === UI: Dashboard ===
@login_required
def dashboard(request):
    try:
        latest = DeviceData.objects.latest("last_seen")
        context = {
            "heart_rate": latest.heart_rate,
            "temperature": latest.temperature,
            "bp_systolic": latest.bp_systolic,
            "bp_diastolic": latest.bp_diastolic,
            "latitude": latest.latitude,
            "longitude": latest.longitude,
            "timestamp": latest.timestamp,
            "is_online": latest.is_online(),
        }
    except DeviceData.DoesNotExist:
        context = {
            "heart_rate": "No data",
            "temperature": "No data",
            "bp_systolic": "No data",
            "bp_diastolic": "No data",
            "latitude": "No data",
            "longitude": "No data",
            "timestamp": "No data",
            "is_online": False,
        }
    return render(request, "monitor/dashboard.html", context)


# === UI: History ===
@login_required
def history_view(request):
    history = SensorHistory.objects.all().order_by("-timestamp")
    return render(request, "history.html", {"history": history})


def location_page(request):
    return render(request, "location.html")


def check_and_create_notification(data):
    alerts = []

    if data["heart_rate"] < 60 or data["heart_rate"] > 120:
        alerts.append("Abnormal heart rate detected.")

    if data["temperature"] < 35 or data["temperature"] > 38:
        alerts.append("Abnormal body temperature detected.")

    if (
        data["bp_systolic"] > 130
        or data["bp_systolic"] < 90
        or data["bp_diastolic"] > 90
        or data["bp_diastolic"] < 60
    ):
        alerts.append("Abnormal blood pressure detected.")

    if alerts:
        Notification.objects.create(
            message=" | ".join(alerts),
            heart_rate=data["heart_rate"],
            temperature=data["temperature"],
            bp_systolic=data["bp_systolic"],
            bp_diastolic=data["bp_diastolic"],
        )


def notification_history(request):
    notifications = Notification.objects.filter(
        Q(heart_rate__lt=60)
        | Q(heart_rate__gt=120)
        | Q(temperature__lt=35)
        | Q(temperature__gt=38)
        | Q(bp_systolic__gt=130)
        | Q(bp_systolic__lt=90)
        | Q(bp_diastolic__gt=90)
        | Q(bp_diastolic__lt=60)
    ).order_by("-timestamp")

    return render(request, "notifications.html", {"notifications": notifications})
