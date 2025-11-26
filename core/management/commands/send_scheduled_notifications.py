from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Notification, DeviceToken
from firebase_admin import messaging

class Command(BaseCommand):
    help = "Send scheduled notifications"

    def handle(self, *args, **kwargs):
        now = timezone.now()

        notifications = Notification.objects.filter(
            is_sent=False,
            scheduled_at__lte=now
        ).select_related("user")

        sent_count = 0

        for n in notifications:
            borrower = n.user

            token_entry = DeviceToken.objects.filter(user=borrower).last()
            if not token_entry:
                continue

            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=n.title,
                        body=n.message
                    ),
                    token=token_entry.token
                )

                messaging.send(message)
                n.is_sent = True
                n.save()
                sent_count += 1

            except Exception as e:
                print("Error sending notification:", e)

        print(f"Sent {sent_count} notifications.")
