import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Health, Job, JobPage, Tool } from "@/lib/types";

export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: () => api<Health>("/health"), staleTime: 30_000, refetchInterval: 30_000 });

export const useJobs = (page: number, workspaceId?: number) =>
  useQuery({
    queryKey: ["jobs", page, workspaceId ?? "mine"],
    queryFn: () => api<JobPage>(`/jobs?page=${page}${workspaceId ? `&workspace_id=${workspaceId}` : ""}`),
    refetchInterval: (q) => q.state.data?.items.some(job => job.status === "queued" || job.status === "processing") ? 3000 : false,
    refetchOnWindowFocus: true,
  });

export const useJob = (id: number) =>
  useQuery({
    queryKey: ["job", id],
    queryFn: () => api<Job>(`/jobs/${id}`),
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return !s || s === "queued" || s === "processing" ? 2000 : false;
    },
    refetchOnWindowFocus: true,
  });

export function useCreateJob() {
  const qc = useQueryClient();
  return useMutation({
    // La clave de idempotencia la crea la página una vez por intención (RF-09)
    mutationFn: (b: { image_id: number; preset: string; key: string; tool?: Tool; params?: Record<string, unknown> }) =>
      api<Job>("/jobs", { method: "POST", headers: { "Idempotency-Key": b.key },
                          body: JSON.stringify({ image_id: b.image_id, preset: b.preset, tool: b.tool ?? "humanizar", params: b.params ?? {} }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

export function useRetryJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { id: number; key: string }) => api<Job>(`/jobs/${b.id}/retry`, {
      method: "POST", headers: { "Idempotency-Key": b.key },
    }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}
