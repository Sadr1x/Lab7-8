from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import localdate

from .models import Repair


def repairs_received_today():
    return Repair.objects.filter(received_on=localdate())


def email_ready_notice(repair):
    return send_mail(
        "Велосипед готовий до видачі",
        f"Ремонт {repair.ticket} завершено.",
        settings.DEFAULT_FROM_EMAIL,
        [repair.bicycle.customer.email],
    )
