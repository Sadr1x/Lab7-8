from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from flask_migrate import upgrade
from sqlalchemy import extract, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from . import create_app
from .models import Bicycle, Customer, Inspection, Repair, Service, db


def demonstrate():
    customer = Customer(name="Demo Rider", email="demo-workshop@example.test")
    bicycle = Bicycle(customer=customer, serial_code="DEMO-11", model_name="City")
    brake_service = Service(code="brakes-demo", name="Brake tune", price=400)
    first = Repair(ticket="DW-351", bicycle=bicycle, problem="Brake rub", received_on=date(2026, 5, 2))
    second = Repair(
        ticket="DW-352", bicycle=bicycle, problem="Loose chain", received_on=date(2026, 4, 28),
        state="done",
    )
    first.services.append(brake_service)
    first.inspection = Inspection(mechanic="Oksana", duration_minutes=20)
    db.session.add_all([first, second])
    db.session.commit()
    print(f"CREATE: {first}, {second}")
    print(f"READ: {db.session.get(Repair, first.id)}")

    tickets = db.select(Repair.ticket).where(Repair.bicycle_id == bicycle.id).order_by(Repair.ticket)
    print(f"FILTER: {list(db.session.scalars(tickets.where(Repair.state == 'queued')))}")
    outside_april = tickets.where(extract("month", Repair.received_on) != 4)
    print(f"EXCLUDE: {list(db.session.scalars(outside_april))}")
    matches = tickets.where(or_(Repair.problem.icontains("brake"), Repair.state == "done"))
    print(f"OR: {list(db.session.scalars(matches))}")
    totals = (
        db.select(func.count(Repair.id), func.avg(Inspection.duration_minutes))
        .outerjoin(Repair.inspection).where(Repair.bicycle_id == bicycle.id)
    )
    count, average = db.session.execute(totals).one()
    print(f"AGGREGATE: {dict(total=count, mean_minutes=average)}")
    grouped = (
        db.select(Bicycle.id, func.count(Repair.id)).join(Bicycle.repairs)
        .where(Bicycle.id == bicycle.id).group_by(Bicycle.id)
    )
    print(f"GROUP BY: {db.session.execute(grouped).one()[1]}")
    related = (
        db.select(Repair).where(Repair.bicycle_id == bicycle.id).order_by(Repair.ticket)
        .options(joinedload(Repair.bicycle), joinedload(Repair.inspection), selectinload(Repair.services))
    )
    for row in db.session.scalars(related):
        if row.inspection is not None:
            print(f"RELATED: {row.ticket}: {row.bicycle.model_name}, {row.inspection.duration_minutes} min, "
                  f"{[item.name for item in row.services]}")
    print(f"REVERSE: {sorted(repair.ticket for repair in bicycle.repairs)}")

    first.state = "done"
    db.session.commit()
    print(f"UPDATE: {db.session.get(Repair, first.id).state}")
    second_id = second.id
    db.session.delete(second)
    db.session.commit()
    print(f"DELETE: count={db.session.scalar(db.select(func.count()).select_from(Repair))}, "
          f"removed_exists={db.session.get(Repair, second_id) is not None}")

    db.session.add(Service(code="temporary", name="Temporary service", price=20))
    try:
        db.session.flush()
        db.session.add(Repair(
            ticket=first.ticket, bicycle=bicycle, problem="Duplicate", received_on=date(2026, 5, 2),
        ))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
    else:
        raise AssertionError("Expected the duplicate ticket to violate uniqueness")
    after = db.session.scalar(db.select(func.count()).select_from(Service).filter_by(code="temporary"))
    print(f"ROLLBACK: duplicate ticket, temporary services={after}")


if __name__ == "__main__":
    with TemporaryDirectory() as temp:
        database = Path(temp) / "demo.sqlite3"
        app = create_app({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{database.as_posix()}"})
        migration_dir = Path(__file__).resolve().parents[1] / "migrations"
        with app.app_context():
            upgrade(directory=str(migration_dir))
            demonstrate()
