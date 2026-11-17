import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Member, Overview, TeamStats, Workspace } from "@/lib/types";

export const useWorkspaces = () => useQuery({ queryKey: ["workspaces"], queryFn: () => api<Workspace[]>("/workspaces") });

export const useMembers = (teamId?: number) =>
  useQuery({ queryKey: ["members", teamId], queryFn: () => api<Member[]>(`/teams/${teamId}/members`), enabled: !!teamId });

export const useTeamStats = (teamId: number | undefined, days: number) =>
  useQuery({ queryKey: ["stats", teamId, days], queryFn: () => api<TeamStats>(`/teams/${teamId}/stats?days=${days}`), enabled: !!teamId });

function useInvalidateTeam() {
  const qc = useQueryClient();
  return () => ["workspaces", "members", "stats", "jobs"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
}

export function useCreateTeam() {
  const inv = useInvalidateTeam();
  return useMutation({ mutationFn: (name: string) => api("/teams", { method: "POST", body: JSON.stringify({ name }) }), onSuccess: inv });
}

export const useInvite = () =>
  useMutation({ mutationFn: (data: { teamId: number; email?: string; display_name?: string }) => api<{ link: string; expires_at: string }>(`/teams/${data.teamId}/invitations`, { method: "POST", body: JSON.stringify(data) }) });

export function useAcceptInvite() {
  const inv = useInvalidateTeam();
  return useMutation({ mutationFn: (token: string) => api("/invitations/accept", { method: "POST", body: JSON.stringify({ token }) }), onSuccess: inv });
}

export function useRemoveMember() {
  const inv = useInvalidateTeam();
  return useMutation({
    mutationFn: (b: { teamId: number; userId: number }) => api(`/teams/${b.teamId}/members/${b.userId}`, { method: "DELETE" }),
    onSuccess: inv,
  });
}

export const useOverview = () =>
  useQuery({ queryKey: ["overview"], queryFn: () => api<Overview>("/admin/overview"), refetchInterval: 10_000, retry: false });

export function useResolveIncident() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api(`/admin/incidents/${id}`, { method: "PATCH", body: JSON.stringify({ status: "resolved" }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["overview"] }),
  });
}
