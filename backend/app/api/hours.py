"""Horario y horas: horario semanal, marcación de entrada/salida, registros manuales y resúmenes."""
import csv
import io
from datetime import date, datetime, timedelta

from flask import Blueprint, Response, g, request
from sqlalchemy.exc import IntegrityError

from . import fail, ok
from ..extensions import db, utc_now
from ..models import TeamMembership, TimeEntry, User, WorkSchedule, audit
from ..services import hours_service
from ..services.hours_service import (DIAS, entry_json, open_entry, overlaps, parse_hhmm, schedule_json, summary, tz)
from ..services.permission_service import login_required, membership_of

bp = Blueprint("hours", __name__)


def now_local():
    return hours_service.now_local()          # se resuelve en tiempo de llamada (las pruebas fijan la hora)


def _ref_date():
    raw = request.args.get("date")
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _period():
    return "month" if request.args.get("period") == "month" else "week"


# ---------- Horario semanal ----------
@bp.get("/hours/schedule")
@login_required
def get_schedule():
    return ok(schedule_json(g.user.id))


@bp.put("/hours/schedule")
@login_required
def put_schedule():
    days = (request.get_json(silent=True) or {}).get("days")
    if not isinstance(days, list) or len(days) > 7:
        return fail("datos_invalidos", "Envía la lista de días del horario.", 400)
    rows, seen = [], set()
    for d in days:
        try:
            wd = int(d.get("weekday"))
        except (TypeError, ValueError, AttributeError):
            return fail("datos_invalidos", "Día inválido.", 400)
        if not 0 <= wd <= 6 or wd in seen:
            return fail("datos_invalidos", "Día inválido o repetido.", 400)
        seen.add(wd)
        s, e = parse_hhmm(d.get("start")), parse_hhmm(d.get("end"))
        if not s or not e or e <= s:
            return fail("datos_invalidos", f"Revisa el horario del {DIAS[wd].lower()}: la salida debe ser después de la entrada.", 400)
        rows.append(WorkSchedule(user_id=g.user.id, weekday=wd, start_time=s, end_time=e))
    db.session.query(WorkSchedule).filter_by(user_id=g.user.id).delete()
    db.session.add_all(rows)
    audit(g.user.id, "hours.schedule_update", "user", g.user.id, days=len(rows))
    db.session.commit()
    return ok(schedule_json(g.user.id))


# ---------- Marcación ----------
@bp.get("/hours/status")
@login_required
def status():
    e = open_entry(g.user.id)
    return ok({"open_entry": entry_json(e) if e else None, "now": now_local().isoformat()})


@bp.post("/hours/clock-in")
@login_required
def clock_in():
    if open_entry(g.user.id):
        return fail("jornada_abierta", "Ya marcaste tu entrada. Marca la salida antes de empezar otra jornada.", 409)
    e = TimeEntry(user_id=g.user.id, clock_in=utc_now(), source="web")
    db.session.add(e)
    try:
        db.session.flush()
    except IntegrityError:                         # doble clic: el índice único parcial lo impide
        db.session.rollback()
        return fail("jornada_abierta", "Ya marcaste tu entrada.", 409)
    audit(g.user.id, "hours.clock_in", "time_entry", e.id)
    db.session.commit()
    return ok(entry_json(e), 201)


@bp.post("/hours/clock-out")
@login_required
def clock_out():
    e = open_entry(g.user.id)
    if not e:
        return fail("sin_jornada", "No tienes una entrada marcada.", 409)
    e.clock_out = max(utc_now(), e.clock_in + timedelta(seconds=1))
    audit(g.user.id, "hours.clock_out", "time_entry", e.id)
    db.session.commit()
    return ok(entry_json(e))


# ---------- Registros ----------
@bp.get("/hours/entries")
@login_required
def entries():
    zone = tz()
    today = now_local().date()
    try:
        d0 = date.fromisoformat(request.args.get("from") or (today - timedelta(days=13)).isoformat())
        d1 = date.fromisoformat(request.args.get("to") or today.isoformat())
    except ValueError:
        return fail("datos_invalidos", "Fechas inválidas.", 400)
    if d1 < d0 or (d1 - d0).days > 92:
        return fail("datos_invalidos", "El rango debe ser de hasta 3 meses.", 400)
    rows = (db.session.query(TimeEntry)
            .filter(TimeEntry.user_id == g.user.id,
                    TimeEntry.clock_in >= datetime.combine(d0, datetime.min.time(), zone),
                    TimeEntry.clock_in < datetime.combine(d1 + timedelta(days=1), datetime.min.time(), zone))
            .order_by(TimeEntry.clock_in.desc()).all())
    return ok([entry_json(e) for e in rows])


@bp.post("/hours/entries")
@login_required
def manual_entry():
    """Registro manual (olvido de marcación): exige nota y queda identificado como 'manual'."""
    d = request.get_json(silent=True) or {}
    zone = tz()
    try:
        day = date.fromisoformat(d.get("date") or "")
    except ValueError:
        return fail("datos_invalidos", "Fecha inválida.", 400)
    s, e = parse_hhmm(d.get("start")), parse_hhmm(d.get("end"))
    note = (d.get("note") or "").strip()
    if not s or not e or e <= s:
        return fail("datos_invalidos", "La hora de salida debe ser posterior a la de entrada.", 400)
    if not (5 <= len(note) <= 200):
        return fail("sin_nota", "Explica el motivo del registro manual (5 a 200 caracteres).", 400)
    today = now_local().date()
    start, end = datetime.combine(day, s, zone), datetime.combine(day, e, zone)
    if day > today or end > now_local() or (today - day).days > 31:
        return fail("fecha_no_permitida", "Solo puedes registrar jornadas pasadas de los últimos 31 días.", 400)
    if overlaps(g.user.id, start, end):
        return fail("se_superpone", "Ese horario se cruza con otra marcación.", 409)
    entry = TimeEntry(user_id=g.user.id, clock_in=start, clock_out=end, source="manual", note=note)
    db.session.add(entry)
    db.session.flush()
    audit(g.user.id, "hours.manual_entry", "time_entry", entry.id)
    db.session.commit()
    return ok(entry_json(entry), 201)


@bp.delete("/hours/entries/<int:entry_id>")
@login_required
def delete_entry(entry_id):
    e = db.session.get(TimeEntry, entry_id)
    if not e or e.user_id != g.user.id:
        return fail("no_encontrado", "No encontrado.", 404)
    if e.source != "manual":
        return fail("no_permitido", "Las marcaciones automáticas no se pueden borrar; solo los registros manuales.", 403)
    db.session.delete(e)
    audit(g.user.id, "hours.manual_delete", "time_entry", entry_id)
    db.session.commit()
    return ok({"deleted": entry_id})


@bp.get("/hours/summary")
@login_required
def my_summary():
    return ok(summary(g.user.id, _period(), _ref_date()))


# ---------- Equipo (propietario) y administrador ----------
def _team_members_or_error(team_id):
    m = membership_of(g.user)
    is_owner = m and m.team_workspace_id == team_id and m.role == "owner"
    if not (is_owner or g.user.global_role == "admin"):
        return None
    return (db.session.query(TeamMembership, User).join(User, User.id == TeamMembership.user_id)
            .filter(TeamMembership.team_workspace_id == team_id).order_by(User.display_name).all())


@bp.get("/teams/<int:team_id>/hours")
@login_required
def team_hours(team_id):
    rows = _team_members_or_error(team_id)
    if rows is None:
        return fail("no_encontrado", "Solo el propietario del equipo puede ver las horas de los integrantes.", 404)
    out = []
    for m, u in rows:
        s = summary(u.id, _period(), _ref_date())
        out.append({"user_id": u.id, "display_name": u.display_name, "role": m.role,
                    "weekly_hours": schedule_json(u.id)["weekly_hours"],
                    **{k: s[k] for k in ("from", "to", "expected_to_date", "worked", "balance", "to_recover")},
                    "working_now": open_entry(u.id) is not None})
    return ok(out)


@bp.get("/teams/<int:team_id>/hours.csv")
@login_required
def team_hours_csv(team_id):
    rows = _team_members_or_error(team_id)
    if rows is None:
        return fail("no_encontrado", "No encontrado.", 404)
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")                  # ';' abre bien en Excel con configuración regional de Perú
    w.writerow(["Trabajador", "Desde", "Hasta", "Horas esperadas a la fecha", "Horas trabajadas", "Saldo", "Por recuperar"])
    for _, u in rows:
        s = summary(u.id, _period(), _ref_date())
        w.writerow([u.display_name, s["from"], s["to"], *(str(s[k]).replace(".", ",") for k in
                    ("expected_to_date", "worked", "balance", "to_recover"))])
    audit(g.user.id, "hours.export", "workspace", team_id)
    db.session.commit()
    return Response("﻿" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=horas_equipo_{team_id}.csv"})
