from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Avg, Count, Q

from repairdesk.models import Bicycle, Customer, Inspection, Repair, Service


class Command(BaseCommand):
    help = "Показує CRUD і запити майстерні в транзакції з фінальним відкатом"

    @transaction.atomic
    def handle(self, *args, **options):
        write = self.stdout.write
        customer = Customer.objects.create(name="Demo Rider", email="demo-workshop@example.test")
        bicycle = Bicycle.objects.create(customer=customer, serial_code="DEMO-11", model_name="City")
        service = Service.objects.create(code="brakes-demo", name="Brake tune", price=400)
        first = Repair.objects.create(
            ticket="DW-351", bicycle=bicycle, problem="Brake rub", received_on=date(2026, 5, 2),
        )
        second = Repair.objects.create(
            ticket="DW-352", bicycle=bicycle, problem="Loose chain", received_on=date(2026, 4, 28),
            state=Repair.State.DONE,
        )
        first.services.add(service)
        Inspection.objects.create(repair=first, mechanic="Oksana", duration_minutes=20)
        repairs = Repair.objects.filter(bicycle=bicycle).order_by("ticket")
        write(f"CREATE: {first}, {second}")
        write(f"READ: {repairs.get(pk=first.pk)}")
        queued = repairs.filter(state=Repair.State.QUEUED).values_list("ticket", flat=True)
        write(f"FILTER: {list(queued)}")
        excluded = repairs.exclude(received_on__month=4).values_list("ticket", flat=True)
        write(f"EXCLUDE: {list(excluded)}")
        selected = repairs.filter(
            Q(problem__icontains="brake") | Q(state=Repair.State.DONE),
        ).values_list("ticket", flat=True)
        write(f"OR: {list(selected)}")
        write(f"AGGREGATE: {repairs.aggregate(total=Count('pk'), mean_minutes=Avg('inspection__duration_minutes'))}")
        bicycle_total = Bicycle.objects.annotate(repair_total=Count("repairs")).get(pk=bicycle.pk)
        write(f"ANNOTATE: {bicycle_total.repair_total}")
        rows = repairs.select_related("bicycle", "inspection").prefetch_related("services")
        details = [
            f"{row.ticket}: {row.bicycle.model_name}, {row.inspection.duration_minutes} min, "
            f"{[item.name for item in row.services.all()]}"
            for row in rows if hasattr(row, "inspection")
        ]
        write(f"RELATED: {details[0]}")
        write(f"REVERSE: {list(bicycle.repairs.order_by('ticket').values_list('ticket', flat=True))}")
        first.state = Repair.State.DONE
        first.save(update_fields=["state"])
        write(f"UPDATE: {Repair.objects.get(pk=first.pk).state}")
        second_pk = second.pk
        second.delete()
        write(f"DELETE: count={repairs.count()}, removed_exists={repairs.filter(pk=second_pk).exists()}")
        transaction.set_rollback(True)
        write("CLEANUP: demonstration transaction rolled back")
