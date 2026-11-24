from datetime import date
from unittest.mock import patch

from repairdesk.services import email_ready_notice, repairs_received_today


@patch("repairdesk.services.send_mail", return_value=1)
def test_email_backend_is_isolated(send, django_repair, settings):
    settings.DEFAULT_FROM_EMAIL = "workshop@example.test"
    assert email_ready_notice(django_repair) == 1
    send.assert_called_once_with(
        "Велосипед готовий до видачі", "Ремонт REP-031 завершено.",
        "workshop@example.test", ["maria@example.test"],
    )


@patch("repairdesk.services.localdate", return_value=date(2026, 5, 2))
def test_today_query_uses_local_calendar(local_date, django_repair):
    assert list(repairs_received_today()) == [django_repair]
    local_date.assert_called_once_with()
