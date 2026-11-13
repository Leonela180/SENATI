export type User = { id: number; email: string; display_name: string; role: "user" | "admin" };
export type JobStatus = "queued" | "processing" | "completed" | "failed";
export type Job = {
  id: number; image_id: number; image_filename: string; status: JobStatus; status_label: string;
  preset: string; model_id: string | null; model_version: string | null;
  parameters: Record<string, unknown>; error_code: string | null; error_message: string | null;
  attempt_count: number; visibility: "private" | "team"; is_owner: boolean;
  created_at: string; finished_at: string | null;
};
export type JobPage = { items: Job[]; page: number; pages: number; total: number };
export type ImageInfo = { id: number; filename: string; width: number; height: number; visibility: "private" | "team" };
export type Workspace = { id: number; name: string; kind: "personal" | "team"; role: "owner" | "member" };
export type Member = { user_id: number; display_name: string; role: "owner" | "member"; joined_at: string };
export type TeamStats = {
  days: number; total: number; completed: number; failed: number; avg_seconds: number | null;
  per_day: { day: string; total: number }[];
};
export type Health = { status: string; engine: "local" | "mock"; presets: string[] };
export type Overview = {
  api: string; database: string; engine: string;
  worker: { seconds_since_beat: number | null; alive: boolean };
  jobs_by_status: Record<JobStatus, number>; avg_seconds_24h: number | null; failed_24h: number; users: number;
  open_incidents: { id: number; service_name: string; error_code: string; occurred_at: string }[];
};
