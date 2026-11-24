from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25, blank=True, default="")

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "клієнт"
        verbose_name_plural = "клієнти"

    def __str__(self):
        return self.name


class Bicycle(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="bicycles")
    serial_code = models.CharField(max_length=30, unique=True)
    model_name = models.CharField(max_length=80)
    color = models.CharField(max_length=30, blank=True, default="")

    class Meta:
        ordering = ["serial_code"]
        verbose_name = "велосипед"
        verbose_name_plural = "велосипеди"

    def __str__(self):
        return f"{self.model_name} ({self.serial_code})"


class Service(models.Model):
    code = models.SlugField(max_length=25, unique=True)
    name = models.CharField(max_length=80)
    price = models.PositiveIntegerField(help_text="Ціна в гривнях")

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "послуга"
        verbose_name_plural = "послуги"

    def __str__(self):
        return self.name


class Repair(models.Model):
    class State(models.TextChoices):
        QUEUED = "queued", "У черзі"
        DONE = "done", "Завершено"

    ticket = models.CharField(max_length=16, unique=True)
    bicycle = models.ForeignKey(Bicycle, on_delete=models.PROTECT, related_name="repairs")
    problem = models.CharField(max_length=140)
    received_on = models.DateField()
    state = models.CharField(max_length=10, choices=State.choices, default=State.QUEUED)
    services = models.ManyToManyField(Service, related_name="repairs", blank=True)

    class Meta:
        ordering = ["-received_on", "ticket"]
        verbose_name = "ремонт"
        verbose_name_plural = "ремонти"

    def __str__(self):
        return self.ticket


class Inspection(models.Model):
    repair = models.OneToOneField(Repair, on_delete=models.CASCADE, related_name="inspection")
    mechanic = models.CharField(max_length=80)
    duration_minutes = models.PositiveIntegerField()
    note = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["repair_id"]
        verbose_name = "огляд"
        verbose_name_plural = "огляди"

    def __str__(self):
        return f"{self.repair.ticket}: {self.mechanic}"
