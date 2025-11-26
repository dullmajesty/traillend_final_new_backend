import os
import time
import django

# --------------------------------------------
# DJANGO SETUP
# --------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traillend_final_web.settings")
django.setup()

from django.utils import timezone
from firebase_admin import messaging
from core.models import Notification, DeviceToken
from core.firebase import initialize_firebase


# --------------------------------------------
# INITIALIZE FIREBASE
# --------------------------------------------
initialize_firebase()


# --------------------------------------------
# SEND DUE NOTIFICATIONS
# --------------------------------------------
def send_due_notifications():
    now = timezone.now()

    # Find scheduled notifications that are due
    due_notifications = Notification.objects.filter(
        is_sent=False,
        scheduled_at__lte=now
    ).select_related("user")

    if not due_notifications.exists():
        print(f"[{now}] No scheduled notifications to send.")
        return

    print(f"[{now}] Sending {due_notifications.count()} scheduled notifications...")

    for notif in due_notifications:
        try:
            # Get the device token for this user
            token_entry = DeviceToken.objects.filter(user=notif.user).last()
            if not token_entry:
                print(f"⚠ User {notif.user.full_name} has no device token.")
                continue

            # Create FCM message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notif.title,
                    body=notif.message
                ),
                token=token_entry.token
            )

            # Send the message
            messaging.send(message)

            # Mark as sent
            notif.is_sent = True
            notif.save()

            print(f"✔ Sent notification → {notif.user.full_name}")

        except Exception as e:
            print(f"❌ Error sending notification for {notif.user.full_name}: {e}")


# --------------------------------------------
# WORKER LOOP
# --------------------------------------------
def run_worker():
    print("🔔 Notification Worker Started (checking every 60 seconds)...")

    while True:
        try:
            send_due_notifications()
        except Exception as e:
            print(f"❌ Worker error: {e}")

        time.sleep(60)  # Sleep for 1 minute


# --------------------------------------------
# START WORKER
# --------------------------------------------
if __name__ == "__main__":
    run_worker()
