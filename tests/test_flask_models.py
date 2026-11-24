from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from workshop_api.models import Inspection, Repair, Service, db


def test_labels_defaults_and_relations(app, api_repair):
    with app.app_context():
        repair = db.session.get(Repair, api_repair)
        assert str(repair) == "REP-031"
        assert str(repair.bicycle) == "Tour (BC-001)"
        assert str(repair.bicycle.customer) == "Maria"
        assert str(repair.services[0]) == "Brake cleaning"
        assert str(repair.inspection) == "REP-031: Olha"
        assert repair.state == "queued"
        assert repair.inspection.note == ""
        assert repair.bicycle.repairs == [repair]
        assert repair.services[0].repairs == [repair]


def test_unique_ticket(app, api_repair):
    with app.app_context():
        repair = db.session.get(Repair, api_repair)
        db.session.add(Repair(
            ticket=repair.ticket, problem="Duplicate", received_on=repair.received_on,
            bicycle=repair.bicycle,
        ))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_requires_existing_bicycle(app):
    with app.app_context():
        db.session.add(Repair(
            ticket="REP-040", problem="Chain slip", received_on=date(2026, 5, 3), bicycle_id=999,
        ))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_cascade_preserves_service_and_removes_inspection(app, api_repair):
    with app.app_context():
        repair = db.session.get(Repair, api_repair)
        inspection_id = repair.inspection.id
        service_id = repair.services[0].id
        db.session.delete(repair)
        db.session.commit()
        assert db.session.get(Inspection, inspection_id) is None
        assert db.session.get(Service, service_id).repairs == []
