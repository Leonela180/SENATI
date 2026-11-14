import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { HoursSummary, Schedule, TeamHoursRow, TimeEntry } from "@/lib/types";

export const useSchedule = () => useQuery({ queryKey: ["schedule"], queryFn: () => api<Schedule>("/hours/schedule") });
export const useHoursStatus = () =>
  useQuery({ queryKey: ["hours-status"], queryFn: () => api<{ open_entry: TimeEntry | null; now: string }>("/hours/status"), refetchInterval: 60_000 });
export const useHoursSummary = (period: "week" | "month") =>
  useQuery({ queryKey: ["hours-summary", period], queryFn: () => api<HoursSummary>(`/hours/summary?period=${period}`), refetchInterval: 60_000 });
export const useEntries = () => useQuery({ queryKey: ["entries"], queryFn: () => api<TimeEntry[]>("/hours/entries") });
export const useTeamHours = (teamId: number | undefined, enabled: boolean, period: "week" | "month") =>
  useQuery({ queryKey: ["team-hours", teamId, period], queryFn: () => api<TeamHoursRow[]>(`/teams/${teamId}/hours?period=${period}`), enabled: !!teamId && enabled });

function useInvalidate() {
  const qc = useQueryClient();
  return () => ["schedule", "hours-status", "hours-summary", "entries", "team-hours"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
}

export function useClock() {
  const inv = useInvalidate();
  return useMutation({ mutationFn: (action: "clock-in" | "clock-out") => api<TimeEntry>(`/hours/${action}`, { method: "POST" }), onSuccess: inv });
}

export function useSaveSchedule() {
  const inv = useInvalidate();
  return useMutation({
    mutationFn: (days: { weekday: number; start: string; end: string }[]) =>
      api<Schedule>("/hours/schedule", { method: "PUT", body: JSON.stringify({ days }) }),
    onSuccess: inv,
  });
}

export function useManualEntry() {
  const inv = useInvalidate();
  return useMutation({
    mutationFn: (b: { date: string; start: string; end: string; note: string }) =>
      api<TimeEntry>("/hours/entries", { method: "POST", body: JSON.stringify(b) }),
    onSuccess: inv,
  });
}

export function useDeleteEntry() {
  const inv = useInvalidate();
  return useMutation({ mutationFn: (id: number) => api(`/hours/entries/${id}`, { method: "DELETE" }), onSuccess: inv });
}
