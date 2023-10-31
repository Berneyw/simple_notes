import note
from plyer import notification

def send_notification_deadline(task_name):
    notification.notify(
        title="Deadline",
        message=f"Deadline for task '{task_name}' has ended.",
        timeout=5,
        ticker="Deadline ended",
        app_icon="simple_notes/images/simpleNotesLogo2.ico",
    )
