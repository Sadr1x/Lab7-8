from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Repair
from .services import repairs_received_today


def repair_list(request):
    repairs = Repair.objects.all()
    if request.GET.get("today") == "1":
        repairs = repairs_received_today()
    query = request.GET.get("q", "").strip()
    if query:
        repairs = repairs.filter(Q(ticket__icontains=query) | Q(problem__icontains=query))
    repairs = repairs.select_related("bicycle").prefetch_related("services")
    return render(request, "repairdesk/list.html", {"repairs": repairs, "query": query})


def repair_detail(request, pk):
    repairs = Repair.objects.select_related("bicycle", "inspection").prefetch_related("services")
    return render(request, "repairdesk/detail.html", {"repair": get_object_or_404(repairs, pk=pk)})


@login_required
def workbench(request):
    return repair_list(request)
