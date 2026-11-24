import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from repairdesk.models import Inspection, Repair, Service


def test_repair_labels_and_defaults(django_repair):
    assert str(django_repair) == "REP-031"
    assert str(django_repair.bicycle) == "Tour (BC-001)"
    assert str(django_repair.bicycle.customer) == "Maria"
    assert str(django_repair.services.get()) == "Brake cleaning"
    assert str(django_repair.inspection) == "REP-031: Olha"
    assert django_repair.state == Repair.State.QUEUED
    assert django_repair.inspection.note == ""


@pytest.mark.parametrize("length", [1, 140, 141])
def test_problem_maximum_length(django_repair, length):
    django_repair.problem = "x" * length
    if length > 140:
        with pytest.raises(ValidationError, match="problem"):
            django_repair.full_clean()
    else:
        django_repair.full_clean()


def test_duplicate_ticket_is_rejected(django_repair):
    with pytest.raises(IntegrityError), transaction.atomic():
        Repair.objects.create(
            ticket=django_repair.ticket, problem="Chain slip", bicycle=django_repair.bicycle,
            received_on=django_repair.received_on,
        )


def test_relationships_and_unique_inspection(django_repair):
    assert django_repair.bicycle.repairs.get() == django_repair
    assert django_repair.services.get().repairs.get() == django_repair
    with pytest.raises(IntegrityError), transaction.atomic():
        Inspection.objects.create(repair=django_repair, mechanic="Anton", duration_minutes=3)


def test_repair_keeps_bicycle_but_deletes_inspection(django_repair):
    with pytest.raises(ProtectedError):
        django_repair.bicycle.delete()
    inspection_id = django_repair.inspection.pk
    service_id = django_repair.services.get().pk
    django_repair.delete()
    assert not Inspection.objects.filter(pk=inspection_id).exists()
    assert Service.objects.get(pk=service_id).repairs.count() == 0
