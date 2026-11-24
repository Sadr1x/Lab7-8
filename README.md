# Веломайстерня · Лабораторна робота №7–8

Два незалежні застосунки для журналу ремонтів велосипедів. Django відображає HTML-сторінки. Flask надає JSON API. Кожен застосунок має власну базу SQLite.

## Встановлення

Потрібен Python 3.12 або новіший. Виконуйте команди з папки, де лежить `manage.py`.

```sh
python -m venv .venv
```

Windows PowerShell — `& .\.venv\Scripts\Activate.ps1`. Linux або macOS — `source .venv/bin/activate`.

```sh
python -m pip install -r requirements.txt
```

## Django

```sh
python manage.py migrate
python manage.py demo_workshop
python manage.py runserver
```

Журнал відкривається на [127.0.0.1:8000](http://127.0.0.1:8000/). Пошук працює за номером ремонту або описом несправності. Для доступу до `/workbench/` створіть обліковий запис командою `python manage.py createsuperuser` і ввійдіть через форму. Для перевірки міграцій виконайте `python manage.py showmigrations repairdesk` і `python manage.py sqlmigrate repairdesk 0002`.

## Flask

```sh
python -m flask --app workshop_api db upgrade
python -m workshop_api.demo
python -m flask --app workshop_api run
```

Список ремонтів доступний на [127.0.0.1:5000/api/repairs](http://127.0.0.1:5000/api/repairs). Для пошуку використовуйте параметр `q`. Створення ремонту через `POST /api/repairs` приймає JSON з полями `ticket`, `problem`, `received_on` (РРРР-ММ-ДД) і `serial_code` (код наявного велосипеда). База за замовчуванням використовує URI `sqlite:///workshop.sqlite3` та зберігається в папці `instance/`.

Після міграцій журнали порожні. Демонстрації створюють тимчасові записи й друкують фактичний результат запитів у терміналі. Django відкочує демонстраційну транзакцію, Flask використовує окрему тимчасову базу.

## Приклад заповнення журналу

У Django виконайте `python manage.py shell` і введіть:

```python
from datetime import date
from repairdesk.models import Bicycle, Customer, Repair

customer, _ = Customer.objects.get_or_create(email="demo@example.test", defaults={"name": "Олена"})
bike, _ = Bicycle.objects.get_or_create(
    serial_code="SAMPLE-1", defaults={"model_name": "City", "customer": customer},
)
Repair.objects.get_or_create(
    ticket="REP-101",
    defaults={"bicycle": bike, "problem": "Скрип гальм", "received_on": date(2026, 5, 2)},
)
```

Для Flask виконайте `python -m flask --app workshop_api shell` і введіть:

```python
from workshop_api.models import Bicycle, Customer, db

bike = db.session.scalar(db.select(Bicycle).filter_by(serial_code="SAMPLE-1"))
if bike is None:
    customer = db.session.scalar(db.select(Customer).filter_by(email="demo@example.test"))
    if customer is None:
        customer = Customer(name="Олена", email="demo@example.test")
    db.session.add(Bicycle(customer=customer, serial_code="SAMPLE-1", model_name="City"))
    db.session.commit()

```

Після цього надішліть `POST /api/repairs` з `Content-Type: application/json` і таким JSON.

```json
{"ticket":"REP-101","problem":"Скрип гальм","received_on":"2026-05-02","serial_code":"SAMPLE-1"}
```

## PyTest

```sh
python -m pytest -v
python -m pytest -v --cov=repairdesk --cov=workshop_api --cov-report=term-missing
```

Тести ізольовано працюють із тестовими базами. Журнал команд збережено у `verification.txt`.
