from datetime import date

from flask import Blueprint, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from .models import Bicycle, Repair, db

api = Blueprint("api", __name__)


def repair_data(repair):
    return {
        "ticket": repair.ticket,
        "problem": repair.problem,
        "state": repair.state,
        "received_on": repair.received_on.isoformat(),
        "services": sorted(service.code for service in repair.services),
    }


@api.get("/api/repairs")
def list_repairs():
    statement = db.select(Repair).options(selectinload(Repair.services))
    query = request.args.get("q", "").strip()
    if query:
        statement = statement.where(or_(
            Repair.ticket.icontains(query, autoescape=True),
            Repair.problem.icontains(query, autoescape=True),
        ))
    statement = statement.order_by(Repair.received_on.desc(), Repair.ticket)
    return [repair_data(repair) for repair in db.session.scalars(statement)]


@api.post("/api/repairs")
def create_repair():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "Очікується JSON-об’єкт."}, 400
    ticket = data.get("ticket")
    problem = data.get("problem")
    serial_code = data.get("serial_code")
    if (
        not isinstance(ticket, str) or not 1 <= len(ticket.strip()) <= 16
        or not isinstance(problem, str) or not 1 <= len(problem.strip()) <= 140
        or not isinstance(serial_code, str) or not 1 <= len(serial_code.strip()) <= 30
    ):
        return {"error": "Перевірте номер, опис і серійний код велосипеда."}, 400
    try:
        received_on = date.fromisoformat(data.get("received_on"))
        if received_on.isoformat() != data["received_on"]:
            raise ValueError("Expected an ISO calendar date with hyphens")
    except (TypeError, ValueError):
        return {"error": "Укажіть дату у форматі РРРР-ММ-ДД."}, 400

    bicycle = db.session.scalar(db.select(Bicycle).filter_by(serial_code=serial_code.strip()))
    if bicycle is None:
        return {"error": "Велосипед не знайдено."}, 404
    repair = Repair(
        ticket=ticket.strip(), bicycle=bicycle, problem=problem.strip(), received_on=received_on,
    )
    db.session.add(repair)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Номер ремонту зайнятий або велосипед недоступний."}, 409
    return repair_data(repair), 201
