import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { QueryError } from "@/components/PageHeader";

type Progress = { user_id: number; display_name: string; shared_images: number; completed: number; queued: number; processing: number; failed: number };

export function TeamProgress({ teamId }: { teamId: number }) {
  const query = useQuery({ queryKey: ["team-progress", teamId], queryFn: () => api<Progress[]>(`/teams/${teamId}/progress`), refetchInterval: 15_000 });
  return <section className="space-y-4 rounded-3xl border bg-card p-6">
    <div><h2 className="font-display text-xl font-semibold">Avance por integrante</h2><p className="mt-1 text-sm text-muted-foreground">Solo cuenta imágenes compartidas con este equipo. Los trabajos privados permanecen privados. Se actualiza automáticamente.</p></div>
    {query.isError ? <QueryError onRetry={() => { void query.refetch(); }} retrying={query.isFetching} /> : query.isLoading ? <p role="status">Consultando avances…</p> : <div className="overflow-x-auto"><table className="w-full text-left text-sm">
      <thead><tr className="border-b text-xs text-muted-foreground"><th className="p-3">Integrante</th><th className="p-3">Compartidas</th><th className="p-3">Completados</th><th className="p-3">En cola</th><th className="p-3">Procesando</th><th className="p-3">Con error</th></tr></thead>
      <tbody>{query.data?.map(row => <tr key={row.user_id} className="border-b last:border-0"><th className="p-3 font-medium">{row.display_name}</th>{[row.shared_images, row.completed, row.queued, row.processing, row.failed].map((count, index) => <td key={index} className="p-3 tabular-nums">{count}</td>)}</tr>)}</tbody>
    </table></div>}
  </section>;
}
