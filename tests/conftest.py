from datetime import date

import pytest
from pytest_django.fixtures import client as web_client
from pytest_flask.fixtures import client as api_client

from repairdesk.models import Bicycle, Customer, Inspection, Repair, Service
from workshop_api import create_app
from workshop_api import models as api_models


@pytest.fixture
def rider_account(db, django_user_model):
    return django_user_model.objects.create_user("mechanic", password="workshop-test")


@pytest.fixture
def django_repair(db):
    customer = Customer.objects.create(name="Maria", email="maria@example.test")
    bicycle = Bicycle.objects.create(customer=customer, serial_code="BC-001", model_name="Tour")
    repair = Repair.objects.create(
        ticket="REP-031", problem="Brake noise", bicycle=bicycle, received_on=date(2026, 5, 2),
    )
    repair.services.add(Service.objects.create(code="brake-clean", name="Brake cleaning", price=300))
    Inspection.objects.create(repair=repair, mechanic="Olha", duration_minutes=12)
    return repair


@pytest.fixture
def app(tmp_path):
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(tmp_path / 'test.sqlite3').as_posix()}",
    })
    with application.app_context():
        api_models.db.create_all()
    yield application
    with application.app_context():
        api_models.db.session.remove()
        api_models.db.engine.dispose()
    (tmp_path / "test.sqlite3").unlink()


@pytest.fixture
def api_repair(app):
    with app.app_context():
        customer = api_models.Customer(name="Maria", email="maria@example.test")
        bicycle = api_models.Bicycle(customer=customer, serial_code="BC-001", model_name="Tour")
        repair = api_models.Repair(
            ticket="REP-031", problem="Brake noise", bicycle=bicycle, received_on=date(2026, 5, 2),
        )
        repair.services.append(api_models.Service(code="brake-clean", name="Brake cleaning", price=300))
        repair.inspection = api_models.Inspection(mechanic="Olha", duration_minutes=12)
        api_models.db.session.add(repair)
        api_models.db.session.commit()
        return repair.id
