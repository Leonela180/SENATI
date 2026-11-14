import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AlarmClock, CalendarClock, Download, LogIn, LogOut, PlusCircle, Trash2, TrendingDown, TrendingUp, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/PageHeader";
import { useWorkspaces } from "@/features/teams/useTeams";
import { useMe } from "@/features/auth/useAuth";
import { useClock, useDeleteEntry, useEntries, useHoursStatus, useHoursSummary, useManualEntry, useSaveSchedule, useSchedule, useTeamHours } from "@/features/hours/useHours";
import { cn } from "@/lib/utils";

const h = (v: number) => {
  const sign = v < 0 ? "−" : "";
  const a = Math.abs(v);
  return `${sign}${Math.floor(a)} h ${String(Math.round((a % 1) * 60)).padStart(2, "0")} min`;
};
const hora = (iso: string) => new Date(iso).toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" });
const dia = (iso: string) => new Date(iso).toLocaleDateString("es-PE", { weekday: "short", day: "2-digit", month: "short" });

function LiveTimer({ since }: { since: string }) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(t); }, []);
  const s = Math.max(0, Math.floor((now - new Date(since).getTime()) / 1000));
  return <span className="font-mono tabular-nums">{String(Math.floor(s / 3600)).padStart(2, "0")}:{String(Math.floor((s % 3600) / 60)).padStart(2, "0")}:{String(s % 60).padStart(2, "0")}</span>;
}

export default function Hours() {
  const [period, setPeriod] = useState<"week" | "month">("week");
  const { data: me } = useMe();
  const { data: status } = useHoursStatus();
  const { data: sum } = useHoursSummary(period);
  const { data: schedule } = useSchedule();
  const { data: entries } = useEntries();
  const { data: workspaces } = useWorkspaces();
  const team = workspaces?.find((w) => w.kind === "team");
  const canSeeTeam = team?.role === "owner" || me?.role === "admin";
  const { data: teamRows } = useTeamHours(team?.id, !!canSeeTeam, period);
  const clock = useClock();
  const saveSchedule = useSaveSchedule();
  const manual = useManualEntry();
  const delEntry = useDeleteEntry();
  const [days, setDays] = useState<{ on: boolean; start: string; end: string }[]>([]);
  const [m, setM] = useState({ date: "", start: "08:00", end: "13:00", note: "" });

  useEffect(() => {
    // Sin horario guardado: se propone lunes a viernes de 08:00 a 13:00 (se confirma con «Guardar horario»)
    if (schedule) setDays(schedule.days.map((d) => ({ on: schedule.weekly_hours ? !!d.start : d.weekday < 5, start: d.start ?? "08:00", end: d.end ?? "13:00" })));
  }, [schedule]);

  const open = status?.open_entry;
  const max = Math.max(1, ...(sum?.days.map((d) => Math.max(d.expected, d.worked)) ?? [1]));

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Horas" title="Horario y horas" description="Marca tu entrada y salida, revisa cuántas horas llevas y si tienes horas por recuperar."
                  action={
                    <div className="inline-flex rounded-full border bg-card p-1" role="group" aria-label="Periodo">
                      {(["week", "month"] as const).map((p) => (
                        <button key={p} onClick={() => setPeriod(p)} aria-pressed={period === p}
                                className={cn("rounded-full px-4 py-1.5 text-sm", period === p ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground")}>
                          {p === "week" ? "Semana" : "Mes"}
                        </button>
                      ))}
                    </div>
                  } />

      {/* Marcación + resumen */}
      <div className="grid gap-6 lg:grid-cols-[22rem_minmax(0,1fr)]">
        <section className={cn("flex flex-col justify-between gap-6 rounded-3xl p-6 shadow-sm", open ? "bg-primary text-primary-foreground" : "border bg-card")}>
          <div className="space-y-1">
            <p className={cn("flex items-center gap-2 text-sm", open ? "text-primary-foreground/80" : "text-muted-foreground")}><AlarmClock className="size-4" aria-hidden />{open ? "Jornada en curso" : "Fuera de jornada"}</p>
            <p className="font-display text-4xl font-semibold">{open ? <LiveTimer since={open.clock_in} /> : "00:00:00"}</p>
            {open && <p className="text-sm text-primary-foreground/80">Entrada a las {hora(open.clock_in)}</p>}
          </div>
          <Button size="lg" variant={open ? "secondary" : "default"} className="h-14 rounded-2xl text-base" disabled={clock.isPending}
                  onClick={() => clock.mutate(open ? "clock-out" : "clock-in", { onSuccess: () => toast.success(open ? "Salida registrada" : "Entrada registrada") })}>
            {open ? <><LogOut className="size-5" aria-hidden />Marcar salida</> : <><LogIn className="size-5" aria-hidden />Marcar entrada</>}
          </Button>
          {clock.error && <p role="alert" className="text-sm">{(clock.error as Error).message}</p>}
        </section>

        <section className="space-y-5 rounded-3xl border bg-card p-6 shadow-sm">
          <div className="grid gap-4 sm:grid-cols-4">
            <div><p className="text-xs text-muted-foreground">Esperadas a la fecha</p><p className="text-xl font-semibold">{sum ? h(sum.expected_to_date) : "—"}</p></div>
            <div><p className="text-xs text-muted-foreground">Trabajadas</p><p className="text-xl font-semibold">{sum ? h(sum.worked) : "—"}</p></div>
            <div><p className="text-xs text-muted-foreground">Saldo</p>
              <p className={cn("flex items-center gap-1 text-xl font-semibold", sum && (sum.balance >= 0 ? "text-emerald-700" : "text-red-700"))}>
                {sum && (sum.balance >= 0 ? <TrendingUp className="size-5" aria-hidden /> : <TrendingDown className="size-5" aria-hidden />)}{sum ? h(sum.balance) : "—"}</p></div>
            <div className={cn("rounded-2xl p-3", sum && sum.to_recover > 0 ? "bg-red-50" : "bg-emerald-50")}>
              <p className="text-xs text-muted-foreground">Por recuperar</p>
              <p className={cn("text-xl font-semibold", sum && sum.to_recover > 0 ? "text-red-800" : "text-emerald-800")}>{sum ? (sum.to_recover > 0 ? h(sum.to_recover) : "Nada 🎉") : "—"}</p>
            </div>
          </div>
          <div>
            <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
              <span>{sum ? `${sum.from} al ${sum.to}` : ""} · total del periodo: {sum ? h(sum.expected_total) : "—"}</span>
              <span className="flex gap-3"><span className="flex items-center gap-1"><span className="size-2 rounded-full bg-muted-foreground/30" />Esperadas</span><span className="flex items-center gap-1"><span className="size-2 rounded-full bg-brand" />Trabajadas</span></span>
            </div>
            <div className={cn("flex h-36 items-end", period === "week" ? "gap-4" : "gap-[3px]")} role="img" aria-label="Horas esperadas y trabajadas por día">
              {sum?.days.map((d) => (
                <div key={d.date} className="flex h-full flex-1 flex-col items-center justify-end gap-1" title={`${d.day} ${d.date}: ${d.worked} h de ${d.expected} h`}>
                  <div className="flex h-full w-full items-end justify-center gap-[2px]">
                    <div className="w-1/2 rounded-t bg-muted-foreground/25" style={{ height: `${(d.expected / max) * 100}%` }} />
                    <div className="w-1/2 rounded-t bg-brand" style={{ height: `${(d.worked / max) * 100}%` }} />
                  </div>
                  {period === "week" && <span className="text-[11px] text-muted-foreground">{d.day.slice(0, 3)}</span>}
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Horario semanal */}
        <section className="space-y-4 rounded-3xl border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 font-semibold"><CalendarClock className="size-5 text-brand-strong" aria-hidden />Mi horario semanal</h2>
            <span className="text-sm text-muted-foreground">{schedule ? (schedule.weekly_hours ? `${schedule.weekly_hours} h por semana` : "Aún sin guardar") : ""}</span>
          </div>
          <div className="space-y-2">
            {schedule?.days.map((d, i) => days[i] && (
              <div key={d.weekday} className="grid grid-cols-[5.2rem_1fr_1fr] items-center gap-2 sm:grid-cols-[7rem_1fr_1fr] sm:gap-3">
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={days[i].on} onChange={(e) => setDays(days.map((x, j) => (j === i ? { ...x, on: e.target.checked } : x)))} className="accent-[oklch(0.27_0.03_40)]" />
                  <span className="sm:hidden">{d.day.slice(0, 3)}</span><span className="hidden sm:inline">{d.day}</span>
                </label>
                <Input type="time" aria-label={`Entrada ${d.day}`} disabled={!days[i].on} value={days[i].start} onChange={(e) => setDays(days.map((x, j) => (j === i ? { ...x, start: e.target.value } : x)))} />
                <Input type="time" aria-label={`Salida ${d.day}`} disabled={!days[i].on} value={days[i].end} onChange={(e) => setDays(days.map((x, j) => (j === i ? { ...x, end: e.target.value } : x)))} />
              </div>
            ))}
          </div>
          {saveSchedule.error && <p role="alert" className="text-sm text-destructive">{(saveSchedule.error as Error).message}</p>}
          <Button className="rounded-xl" disabled={saveSchedule.isPending}
                  onClick={() => saveSchedule.mutate(days.flatMap((d, i) => (d.on ? [{ weekday: i, start: d.start, end: d.end }] : [])), { onSuccess: () => toast.success("Horario guardado") })}>
            Guardar horario
          </Button>
        </section>

        {/* Registros */}
        <section className="space-y-4 rounded-3xl border bg-card p-6 shadow-sm">
          <h2 className="font-semibold">Mis marcaciones (últimos 14 días)</h2>
          <div className="max-h-72 overflow-y-auto">
            {entries?.length ? (
              <table className="w-full text-sm">
                <thead className="text-left text-xs text-muted-foreground"><tr><th className="py-1">Día</th><th>Entrada</th><th>Salida</th><th>Horas</th><th /></tr></thead>
                <tbody>
                  {entries.map((e) => (
                    <tr key={e.id} className="border-t">
                      <td className="py-2">{dia(e.clock_in)}</td><td>{hora(e.clock_in)}</td><td>{e.clock_out ? hora(e.clock_out) : <span className="text-amber-700">en curso</span>}</td>
                      <td>{h(e.hours)}{e.source === "manual" && <span className="ml-2 rounded-full bg-secondary px-2 py-0.5 text-[10px]" title={e.note ?? ""}>manual</span>}</td>
                      <td className="text-right">{e.source === "manual" && <button onClick={() => delEntry.mutate(e.id)} aria-label="Borrar registro manual" className="rounded p-1 text-red-700 hover:bg-red-50"><Trash2 className="size-4" /></button>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <p className="text-sm text-muted-foreground">Aún no tienes marcaciones.</p>}
          </div>
          <form className="space-y-3 border-t pt-4" onSubmit={(e) => { e.preventDefault(); manual.mutate(m, { onSuccess: () => { toast.success("Registro manual guardado"); setM({ ...m, note: "" }); } }); }}>
            <p className="flex items-center gap-2 text-sm font-medium"><PlusCircle className="size-4" aria-hidden />¿Olvidaste marcar? Registro manual</p>
            <div className="grid grid-cols-3 gap-2">
              <Input type="date" required aria-label="Fecha" value={m.date} onChange={(e) => setM({ ...m, date: e.target.value })} />
              <Input type="time" required aria-label="Entrada" value={m.start} onChange={(e) => setM({ ...m, start: e.target.value })} />
              <Input type="time" required aria-label="Salida" value={m.end} onChange={(e) => setM({ ...m, end: e.target.value })} />
            </div>
            <div className="space-y-1"><Label htmlFor="nota">Motivo (obligatorio)</Label>
              <Input id="nota" required minLength={5} maxLength={200} value={m.note} onChange={(e) => setM({ ...m, note: e.target.value })} placeholder="Ej.: olvidé marcar por una reunión fuera" /></div>
            {manual.error && <p role="alert" className="text-sm text-destructive">{(manual.error as Error).message}</p>}
            <Button type="submit" variant="outline" className="rounded-xl" disabled={manual.isPending}>Guardar registro</Button>
          </form>
        </section>
      </div>

      {/* Equipo */}
      {canSeeTeam && team && (
        <section className="space-y-4 rounded-3xl border bg-card p-6 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="flex items-center gap-2 font-semibold"><Users className="size-5 text-brand-strong" aria-hidden />Horas del equipo · {team.name}</h2>
            <Button asChild variant="outline" size="sm" className="rounded-full"><a href={`/api/v1/teams/${team.id}/hours.csv?period=${period}`}><Download className="size-4" aria-hidden />Exportar a Excel (CSV)</a></Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-muted-foreground"><tr><th className="py-2">Trabajador</th><th>Horario semanal</th><th>Esperadas</th><th>Trabajadas</th><th>Saldo</th><th>Por recuperar</th><th>Ahora</th></tr></thead>
              <tbody>
                {teamRows?.map((r) => (
                  <tr key={r.user_id} className="border-t">
                    <td className="py-2 font-medium">{r.display_name}</td><td>{r.weekly_hours} h</td><td>{h(r.expected_to_date)}</td><td>{h(r.worked)}</td>
                    <td className={r.balance >= 0 ? "text-emerald-700" : "text-red-700"}>{h(r.balance)}</td>
                    <td>{r.to_recover > 0 ? <span className="rounded-full bg-red-100 px-2 py-0.5 text-red-900">{h(r.to_recover)}</span> : <span className="text-emerald-700">—</span>}</td>
                    <td>{r.working_now ? <span className="flex items-center gap-1 text-emerald-700"><span className="size-2 rounded-full bg-emerald-600 pulse-dot" />Trabajando</span> : <span className="text-muted-foreground">Fuera</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
