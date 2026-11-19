import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ClipboardCheck } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { QueryError } from "@/components/PageHeader";

type Leave = { id: number; user_id: number; display_name: string; starts_at: string; ends_at: string; reason: string; status: string; review_note: string | null };
const LABELS: Record<string, string> = { pending: "Pendiente", approved: "Aprobado", rejected: "Rechazado", cancelled: "Cancelado" };

export function LeavePanel({ teamId, isOwner }: { teamId: number; isOwner: boolean }) {
  const qc = useQueryClient();
  const [form, setForm] = useState({ starts_at: "", ends_at: "", reason: "" });
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [pendingOnly, setPendingOnly] = useState(false);
  const endpoint = `/teams/${teamId}/leave`;
  const list = useQuery({ queryKey: ["leave", teamId], queryFn: () => api<Leave[]>(endpoint), refetchInterval: 15000 });
  const invalidate = () => qc.invalidateQueries({ queryKey: ["leave", teamId] });
  const send = useMutation({ mutationFn: () => api(endpoint, { method: "POST", body: JSON.stringify({ ...form, starts_at: new Date(form.starts_at).toISOString(), ends_at: new Date(form.ends_at).toISOString() }) }),
    onSuccess: () => { setForm({ starts_at: "", ends_at: "", reason: "" }); void invalidate(); } });
  const review = useMutation({ mutationFn: ({ id, status }: { id: number; status: string }) => api(`${endpoint}/${id}`, { method: "PATCH", body: JSON.stringify({ status, review_note: notes[id] || "" }) }), onSuccess: invalidate });
  const rows = (list.data || []).filter(row => !pendingOnly || row.status === "pending");
  return <section className="space-y-5 rounded-3xl border bg-card p-5 sm:p-7">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><h2 className="flex items-center gap-2 text-lg font-semibold"><ClipboardCheck className="size-5 text-brand-strong" aria-hidden />Permisos del equipo</h2><p className="mt-1 text-sm text-muted-foreground">{isOwner ? "Revisa solicitudes, responde y consulta sus estados. Los motivos son visibles solo para el solicitante y el líder." : "Solicita un permiso y consulta la respuesta del líder."}</p></div><span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium">{isOwner ? "Líder · administrador del equipo" : "Integrante"}</span></div>
    {!isOwner && <form className="grid gap-4 rounded-2xl bg-secondary/40 p-4 sm:grid-cols-2" onSubmit={e => { e.preventDefault(); send.mutate(); }}>
      <label className="space-y-1 text-sm">Desde<Input type="datetime-local" required value={form.starts_at} onChange={e => setForm({ ...form, starts_at: e.target.value })} /></label>
      <label className="space-y-1 text-sm">Hasta<Input type="datetime-local" required value={form.ends_at} min={form.starts_at || undefined} onChange={e => setForm({ ...form, ends_at: e.target.value })} /></label>
      <label className="space-y-1 text-sm sm:col-span-2">Motivo<textarea required minLength={5} maxLength={500} rows={2} value={form.reason} onChange={e => setForm({ ...form, reason: e.target.value })} className="block w-full rounded-xl border bg-background p-3" placeholder="Describe lo necesario para que el líder revise tu solicitud." /></label>
      <Button disabled={send.isPending} className="rounded-xl sm:col-span-2">Solicitar permiso</Button>
    </form>}
    {(send.error || review.error) && <p role="alert" className="text-sm text-destructive">{((send.error || review.error) as Error).message}</p>}
    {send.isSuccess && <p role="status" className="text-sm text-brand-strong">Solicitud registrada. El líder puede revisarla desde Equipo.</p>}
    <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={pendingOnly} onChange={e => setPendingOnly(e.target.checked)} />Solo pendientes</label>
    {list.isPending ? <p role="status" className="text-sm text-muted-foreground">Cargando solicitudes…</p> : list.isError ? <QueryError onRetry={() => { void list.refetch(); }} retrying={list.isFetching} /> : rows.length === 0 ? <p className="rounded-2xl border border-dashed p-5 text-sm text-muted-foreground">No hay solicitudes en esta vista.</p> : <ul className="space-y-4">{rows.map(row => <li key={row.id} className="space-y-3 rounded-2xl border p-4">
      <div className="flex flex-wrap justify-between gap-2"><strong className="text-sm">{row.display_name}</strong><span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium">{LABELS[row.status] || row.status}</span></div>
      <p className="text-xs text-muted-foreground">{new Date(row.starts_at).toLocaleString("es-PE")} — {new Date(row.ends_at).toLocaleString("es-PE")}</p><p className="break-words text-sm">{row.reason}</p>
      {row.review_note && <p className="rounded-xl bg-secondary p-3 text-sm">Respuesta: {row.review_note}</p>}
      {row.status === "pending" && (isOwner ? <div className="space-y-2"><Input aria-label={`Respuesta para ${row.display_name}`} maxLength={300} placeholder="Respuesta o indicación (opcional)" value={notes[row.id] || ""} onChange={e => setNotes({ ...notes, [row.id]: e.target.value })} /><div className="flex gap-2"><Button disabled={review.isPending} size="sm" onClick={() => review.mutate({ id: row.id, status: "approved" })}>Aprobar</Button><Button disabled={review.isPending} size="sm" variant="outline" onClick={() => review.mutate({ id: row.id, status: "rejected" })}>Rechazar</Button></div></div> : <Button disabled={review.isPending} size="sm" variant="outline" onClick={() => review.mutate({ id: row.id, status: "cancelled" })}>Cancelar solicitud</Button>)}
    </li>)}</ul>}
    <p className="text-xs text-muted-foreground">El rol identifica al administrador de este espacio de LUMIA. No acredita un cargo laboral ni representación legal. Estos permisos internos no modifican automáticamente el registro de horas.</p>
  </section>;
}
