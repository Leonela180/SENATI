"""Horario y horas de los trabajadores: horas esperadas según el horario, horas trabajadas y saldo.

Reglas:
- Las horas esperadas salen del horario semanal (un tramo por día).
- Solo cuentan como «esperadas a la fecha» los tramos ya transcurridos (hoy, hasta la hora actual).
- Las horas trabajadas salen de las marcaciones; una jornada abierta cuenta hasta ahora.
- Saldo = trabajadas − esperadas a la fecha. Si es negativo, esas son las horas por recuperar.
"""
from datetime import date, datetime, time, timedelta, timezone

from flask import current_app
from sqlalchemy import or_

from ..extensions import db
from ..models import TimeEntry, WorkSchedule

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def tz():
    return timezone(timedelta(hours=current_app.config["APP_TZ_OFFSET_HOURS"]))


def now_local():
    return datetime.now(tz())


def schedule_of(user_id):
    rows = db.session.query(WorkSchedule).filter_by(user_id=user_id).order_by(WorkSchedule.weekday).all()
    return {r.weekday: (r.start_time, r.end_time) for r in rows}


def schedule_json(user_id):
    sch = schedule_of(user_id)
    days = []
    for wd in range(7):
        if wd in sch:
            s, e = sch[wd]
            days.append({"weekday": wd, "day": DIAS[wd], "start": s.strftime("%H:%M"), "end": e.strftime("%H:%M"),
                         "hours": round(_hours(s, e), 2)})
        else:
            days.append({"weekday": wd, "day": DIAS[wd], "start": None, "end": None, "hours": 0})
    return {"days": days, "weekly_hours": round(sum(d["hours"] for d in days), 2)}


def _hours(start: time, end: time) -> float:
    return (datetime.combine(date.min, end) - datetime.combine(date.min, start)).total_seconds() / 3600


def parse_hhmm(value):
    try:
        h, m = str(value).split(":")
        return time(int(h), int(m))
    except (ValueError, TypeError):
        return None


def period_bounds(period: str, ref: date):
    if period == "month":
        start = ref.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
    else:                                              # semana de lunes a domingo
        start = ref - timedelta(days=ref.weekday())
        end = start + timedelta(days=7)
    return start, end                                  # [start, end)


def _overlap_hours(a0, a1, b0, b1) -> float:
    s, e = max(a0, b0), min(a1, b1)
    return max(0.0, (e - s).total_seconds() / 3600)


def summary(user_id, period="week", ref: date | None = None):
    zone, now = tz(), now_local()
    ref = ref or now.date()
    p0, p1 = period_bounds(period, ref)
    sch = schedule_of(user_id)
    start_dt = datetime.combine(p0, time.min, zone)
    end_dt = datetime.combine(p1, time.min, zone)
    entries = (db.session.query(TimeEntry)
               .filter(TimeEntry.user_id == user_id, TimeEntry.clock_in < end_dt,
                       or_(TimeEntry.clock_out.is_(None), TimeEntry.clock_out > start_dt))
               .order_by(TimeEntry.clock_in).all())
    days, total_exp, exp_to_date, worked = [], 0.0, 0.0, 0.0
    d = p0
    while d < p1:
        d0, d1 = datetime.combine(d, time.min, zone), datetime.combine(d + timedelta(days=1), time.min, zone)
        exp = exp_now = 0.0
        if d.weekday() in sch:
            s, e = sch[d.weekday()]
            s_dt, e_dt = datetime.combine(d, s, zone), datetime.combine(d, e, zone)
            exp = _hours(s, e)
            exp_now = _overlap_hours(s_dt, e_dt, s_dt, min(e_dt, now)) if now > s_dt else 0.0
        w = sum(_overlap_hours(en.clock_in.astimezone(zone), (en.clock_out or now).astimezone(zone), d0, min(d1, now))
                for en in entries)
        days.append({"date": d.isoformat(), "day": DIAS[d.weekday()], "expected": round(exp, 2), "worked": round(w, 2)})
        total_exp, exp_to_date, worked = total_exp + exp, exp_to_date + exp_now, worked + w
        d += timedelta(days=1)
    balance = worked - exp_to_date
    return {"period": period, "from": p0.isoformat(), "to": (p1 - timedelta(days=1)).isoformat(),
            "expected_total": round(total_exp, 2), "expected_to_date": round(exp_to_date, 2),
            "worked": round(worked, 2), "balance": round(balance, 2), "to_recover": round(max(0.0, -balance), 2),
            "days": days}


def open_entry(user_id):
    return db.session.query(TimeEntry).filter_by(user_id=user_id, clock_out=None).first()


def entry_json(e):
    zone = tz()
    cin = e.clock_in.astimezone(zone)
    cout = e.clock_out.astimezone(zone) if e.clock_out else None
    end = cout or now_local()
    return {"id": e.id, "clock_in": cin.isoformat(), "clock_out": cout.isoformat() if cout else None,
            "hours": round((end - cin).total_seconds() / 3600, 2), "source": e.source, "note": e.note, "open": cout is None}


def overlaps(user_id, start, end, exclude_id=None):
    q = db.session.query(TimeEntry).filter(TimeEntry.user_id == user_id, TimeEntry.clock_in < end,
                                           or_(TimeEntry.clock_out.is_(None), TimeEntry.clock_out > start))
    if exclude_id:
        q = q.filter(TimeEntry.id != exclude_id)
    return db.session.query(q.exists()).scalar()
