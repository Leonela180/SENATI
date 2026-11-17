import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { CheckCircle2, Clock, Copy, Link2, Mail, MessageCircle, Users, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/PageHeader";
import { useMe } from "@/features/auth/useAuth";
import { useAcceptInvite, useCreateTeam, useInvite, useMembers, useRemoveMember, useTeamStats, useWorkspaces } from "@/features/teams/useTeams";
import { cn } from "@/lib/utils";

export default function Team() {
  const [params, setParams] = useSearchParams();
  const token = params.get("token");
  const { data: me } = useMe();
  const { data: workspaces } = useWorkspaces();
  const team = workspaces?.find((w) => w.kind === "team");
  const [name, setName] = useState("");
  const [days, setDays] = useState(30);
  const [link, setLink] = useState("");
  const [recipient, setRecipient] = useState({ email: "", display_name: "" });
  const [invitedEmail, setInvitedEmail] = useState("");
  const create = useCreateTeam();
  const accept = useAcceptInvite();
  const invite = useInvite();
  const remove = useRemoveMember();
  const { data: members } = useMembers(team?.id);
  const { data: stats } = useTeamStats(team?.id, days);

  useEffect(() => {
    if (token && workspaces && !team && !accept.isPending && !accept.isSuccess && !accept.isError) {
      accept.mutate(token, { onSuccess: () => { toast.success("Te uniste al equipo"); setParams({}); } });
    }
  }, [token, workspaces, team]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!team) {
    return (
      <div className="space-y-8">
        <PageHeader eyebrow="Equipo" title="Trabaja en equipo" description="Comparte imágenes elegidas con tu equipo y ve estadísticas agregadas del trabajo de todos." />
        {accept.error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{(accept.error as Error).message}</p>}
        <div className="grid gap-6 md:grid-cols-2">
          <form className="space-y-4 rounded-3xl border bg-card p-6 shadow-sm md:p-8" onSubmit={(e) => { e.preventDefault(); create.mutate(name); }}>
            <span className="grid size-10 place-items-center rounded-2xl bg-brand-soft text-brand-strong"><Users className="size-5" aria-hidden /></span>
            <h2 className="font-display text-2xl font-semibold">Crear un equipo</h2>
            <div className="space-y-2"><Label htmlFor="team">Nombre del equipo</Label>
              <Input id="team" required maxLength={120} className="h-11" placeholder="Ej.: Estudio Creativo" value={name} onChange={(e) => setName(e.target.value)} /></div>
            {create.error && <p role="alert" className="text-sm text-destructive">{(create.error as Error).message}</p>}
            <Button type="submit" className="rounded-xl" disabled={create.isPending}>Crear equipo</Button>
          </form>
          <div className="space-y-3 rounded-3xl border border-dashed p-6 md:p-8">
            <span className="grid size-10 place-items-center rounded-2xl bg-muted"><Link2 className="size-5" aria-hidden /></span>
            <h2 className="font-display text-2xl font-semibold">¿Te invitaron?</h2>
            <p className="text-sm text-muted-foreground">Abre el enlace de invitación que te enviaron. Te unirás automáticamente al equipo. Cada enlace sirve una sola vez y vence en 72 horas.</p>
          </div>
        </div>
      </div>
    );
  }

  const isOwner = team.role === "owner";
  // Una barra por día del periodo (los días sin trabajos van en cero), para que el gráfico sea proporcional
  const series = (() => {
    if (!stats) return [];
    const byDay = new Map(stats.per_day.map((d) => [d.day, d.total]));
    return Array.from({ length: stats.days }, (_, i) => {
      const day = new Date(Date.now() - (stats.days - 1 - i) * 86_400_000).toISOString().slice(0, 10);
      return { day, total: byDay.get(day) ?? 0 };
    });
  })();
  const max = Math.max(1, ...series.map((d) => d.total));
  const kpis = [
    { icon: Users, label: "Trabajos", value: stats?.total ?? 0 },
    { icon: CheckCircle2, label: "Completados", value: stats?.completed ?? 0 },
    { icon: XCircle, label: "Fallidos", value: stats?.failed ?? 0 },
    { icon: Clock, label: "Tiempo medio", value: stats?.avg_seconds != null ? `${stats.avg_seconds} s` : "—" },
  ];

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Equipo" title={team.name} description={isOwner ? "Eres el propietario del equipo." : "Eres integrante del equipo."}
                  action={
                    <div className="inline-flex rounded-full border bg-card p-1" role="group" aria-label="Periodo">
                      {[7, 30, 90].map((d) => (
                        <button key={d} onClick={() => setDays(d)} aria-pressed={days === d}
                                className={cn("rounded-full px-4 py-1.5 text-sm", days === d ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground")}>{d} días</button>
                      ))}
                    </div>
                  } />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map(({ icon: Icon, label, value }) => (
          <div key={label} className="rounded-3xl border bg-card p-5 shadow-sm">
            <Icon className="size-5 text-brand-strong" aria-hidden />
            <p className="mt-3 text-xs text-muted-foreground">{label}</p>
            <p className="text-2xl font-semibold">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
        <section className="rounded-3xl border bg-card p-6 shadow-sm">
          <h2 className="font-semibold">Trabajos por día</h2>
          <p className="text-xs text-muted-foreground">Últimos {days} días · solo cifras agregadas</p>
          <div className="mt-6 flex h-44 items-end gap-[3px]" role="img" aria-label={`Trabajos por día en los últimos ${days} días`}>
            {series.map((d) => (
              <div key={d.day} title={`${d.day}: ${d.total}`} className={cn("flex-1 rounded-t-md", d.total ? "bg-brand" : "bg-muted")}
                   style={{ height: d.total ? `${Math.max(6, (d.total / max) * 100)}%` : "4px" }} />
            ))}
          </div>
          <div className="mt-2 flex justify-between text-[11px] text-muted-foreground"><span>{series[0]?.day}</span><span>Hoy</span></div>
        </section>

        <section className="space-y-5 rounded-3xl border bg-card p-6 shadow-sm">
          <h2 className="font-semibold">Integrantes</h2>
          <ul className="space-y-3">
            {members?.map((m) => (
              <li key={m.user_id} className="flex items-center gap-3">
                <span className="grid size-9 shrink-0 place-items-center rounded-full bg-brand-soft text-sm font-semibold text-brand-strong">{m.display_name.charAt(0).toUpperCase()}</span>
                <span className="min-w-0 flex-1"><span className="block truncate text-sm font-medium">{m.display_name}{m.user_id === me?.id && " (tú)"}</span>
                  <span className="text-xs text-muted-foreground">{m.role === "owner" ? "Propietario" : "Integrante"}</span></span>
                {m.role !== "owner" && (isOwner || m.user_id === me?.id) && (
                  <Button size="sm" variant="ghost" onClick={() => remove.mutate({ teamId: team.id, userId: m.user_id })}>
                    {m.user_id === me?.id ? "Salir" : "Retirar"}
                  </Button>
                )}
              </li>
            ))}
          </ul>
          {isOwner && (
            <div className="space-y-2 border-t pt-5">
              <Label htmlFor="invite-name">Nombre de la persona (opcional)</Label>
              <Input id="invite-name" maxLength={120} value={recipient.display_name} onChange={e => setRecipient({ ...recipient, display_name: e.target.value })} />
              <Label htmlFor="invite-email">Correo de la persona (opcional)</Label>
              <Input id="invite-email" type="email" maxLength={254} placeholder="persona@correo.com" value={recipient.email} onChange={e => setRecipient({ ...recipient, email: e.target.value })} />
              <p className="text-xs text-muted-foreground">Si indicas un correo, solo una cuenta con ese correo podrá aceptar. La persona crea su propia contraseña.</p>
              <Button variant="outline" disabled={invite.isPending || (!!recipient.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(recipient.email.trim()))} className="w-full rounded-xl" onClick={() => invite.mutate({ teamId: team.id, ...recipient }, { onSuccess: (d) => { setLink(window.location.origin + d.link); setInvitedEmail(recipient.email.trim()); } })}>
                <Link2 className="size-4" aria-hidden />Generar invitación
              </Button>
              {invite.error && <p role="alert" className="text-sm text-destructive">{(invite.error as Error).message}</p>}
              {link && (
                <div className="space-y-1">
                  <div className="flex gap-2">
                    <Input readOnly value={link} aria-label="Enlace de invitación" onFocus={(e) => e.target.select()} />
                    <Button size="icon" variant="secondary" aria-label="Copiar enlace"
                            onClick={async () => { try { await navigator.clipboard.writeText(link); toast.success("Enlace copiado"); } catch { toast.error("Selecciona y copia el enlace manualmente."); } }}><Copy className="size-4" /></Button>
                  </div>
                  <p className="text-xs text-muted-foreground">Un solo uso, vence en 72 horas. Cópialo ahora: no se vuelve a mostrar.</p>
                  <div className="flex flex-wrap gap-2 pt-2">
                    <Button asChild size="sm" variant="outline"><a href={`mailto:${encodeURIComponent(invitedEmail)}?subject=${encodeURIComponent(`Invitación a ${team.name} en LUMIA`)}&body=${encodeURIComponent(`Te invito a mi equipo en LUMIA AI. Abre este enlace para crear tu cuenta con tu propia contraseña o iniciar sesión. Vence en 72 horas y sirve una vez:\n${link}`)}`}><Mail className="size-4" aria-hidden />Preparar correo</a></Button>
                    <Button asChild size="sm" variant="outline"><a target="_blank" rel="noopener noreferrer" href={`https://wa.me/?text=${encodeURIComponent(`Te invito a ${team.name} en LUMIA AI. Crea tu cuenta o inicia sesión con este enlace de un solo uso (72 horas): ${link}`)}`}><MessageCircle className="size-4" aria-hidden />WhatsApp</a></Button>
                  </div>
                  <p className="text-xs text-muted-foreground">Se abre tu aplicación para revisar y enviar el mensaje. LUMIA no envía correos automáticamente.</p>
                </div>
              )}
            </div>
          )}
          <Link className="block text-sm font-medium text-brand-strong hover:underline" to="/app/historial">Ver imágenes compartidas →</Link>
        </section>
      </div>
    </div>
  );
}
