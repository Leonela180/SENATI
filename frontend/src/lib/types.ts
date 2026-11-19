export type User = { id: number; email: string; display_name: string; role: "user" | "admin" };
export type JobStatus = "queued" | "processing" | "completed" | "failed";
export type Job = {
  id: number; image_id: number; image_filename: string; status: JobStatus; status_label: string;
  preset: string; tool: Tool; tool_label: string; model_id: string | null; model_version: string | null;
  parameters: Record<string, unknown>; error_code: string | null; error_message: string | null;
  attempt_count: number; visibility: "private" | "team"; is_owner: boolean;
  created_at: string; finished_at: string | null;
};
export type JobPage = { items: Job[]; page: number; pages: number; total: number };
export type ImageInfo = {
  id: number; filename: string; width: number; height: number; visibility: "private" | "team";
  album_id?: number | null; created_at?: string; last_job_id?: number | null;
};
export type ImagePage = { items: ImageInfo[]; page: number; pages: number; total: number };
export type Tool = "humanizar" | "quitar_lunar" | "cambiar_fondo" | "desenfoque" | "mejorar_calidad" | "ajustes" | "restaurar" | "textura_piel" | "realista";
export type Album = { id: number; name: string; count: number; created_at: string };
export type Generation = {
  id: number; prompt: string; model: string; status: "completed" | "failed"; image_id: number | null;
  error_code: string | null; seconds: number | null; created_at: string;
};
export type ScheduleDay = { weekday: number; day: string; start: string | null; end: string | null; hours: number };
export type Schedule = { days: ScheduleDay[]; weekly_hours: number };
export type TimeEntry = { id: number; clock_in: string; clock_out: string | null; hours: number; source: "web" | "manual"; note: string | null; open: boolean };
export type HoursSummary = {
  period: "week" | "month"; from: string; to: string; expected_total: number; expected_to_date: number;
  worked: number; balance: number; to_recover: number; days: { date: string; day: string; expected: number; worked: number }[];
};
export type TeamHoursRow = {
  user_id: number; display_name: string; role: "owner" | "member"; weekly_hours: number; from: string; to: string;
  expected_to_date: number; worked: number; balance: number; to_recover: number; working_now: boolean;
};
export type Workspace = { id: number; name: string; kind: "personal" | "team"; role: "owner" | "member" };
export type Member = { user_id: number; display_name: string; role: "owner" | "member"; joined_at: string };
export type TeamStats = {
  days: number; total: number; completed: number; failed: number; avg_seconds: number | null;
  per_day: { day: string; total: number }[];
};
export type Health = { status: string; engine: "local" | "mock"; presets: string[]; runtime?: string; realistic_available?: boolean };
export type Overview = {
  api: string; database: string; engine: string;
  worker: { seconds_since_beat: number | null; alive: boolean };
  jobs_by_status: Record<JobStatus, number>; avg_seconds_24h: number | null; failed_24h: number; users: number;
  open_incidents: { id: number; service_name: string; error_code: string; occurred_at: string }[];
};
