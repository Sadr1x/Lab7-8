import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def enforce_sqlite_foreign_keys(connection, _record):
    if isinstance(connection, sqlite3.Connection):
        with connection as sqlite:
            sqlite.execute("PRAGMA foreign_keys = ON")


repair_services = db.Table(
    "repair_services",
    db.Column("repair_id", db.ForeignKey("repair.id", ondelete="CASCADE"), primary_key=True),
    db.Column("service_id", db.ForeignKey("service.id", ondelete="CASCADE"), primary_key=True),
)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    phone = db.Column(db.String(25), nullable=False, default="")

    def __str__(self):
        return self.name


class Bicycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.ForeignKey("customer.id", ondelete="RESTRICT"), nullable=False,
    )
    serial_code = db.Column(db.String(30), nullable=False, unique=True)
    model_name = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(30), nullable=False, default="")
    customer = db.relationship(Customer, backref=db.backref("bicycles", passive_deletes="all"))

    def __str__(self):
        return f"{self.model_name} ({self.serial_code})"


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(25), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, db.CheckConstraint("price >= 0"), nullable=False)

    def __str__(self):
        return self.name


class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String(16), nullable=False, unique=True)
    bicycle_id = db.Column(db.ForeignKey("bicycle.id", ondelete="RESTRICT"), nullable=False)
    problem = db.Column(db.String(140), nullable=False)
    received_on = db.Column(db.Date, nullable=False)
    state = db.Column(db.String(10), nullable=False, default="queued")
    bicycle = db.relationship(Bicycle, backref=db.backref("repairs", passive_deletes="all"))
    services = db.relationship(Service, secondary=repair_services, backref="repairs")

    def __str__(self):
        return self.ticket


class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.ForeignKey("repair.id", ondelete="CASCADE"), nullable=False, unique=True)
    mechanic = db.Column(db.String(80), nullable=False)
    duration_minutes = db.Column(
        db.Integer, db.CheckConstraint("duration_minutes >= 0"), nullable=False,
    )
    note = db.Column(db.Text, nullable=False, server_default=db.text("''"))
    repair = db.relationship(
        Repair,
        backref=db.backref(
            "inspection", uselist=False, cascade="all, delete-orphan", passive_deletes=True,
        ),
    )

    def __str__(self):
        return f"{self.repair.ticket}: {self.mechanic}"
