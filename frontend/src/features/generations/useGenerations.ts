import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Generation, ImageInfo } from "@/lib/types";

export const useGenerationStatus = () =>
  useQuery({ queryKey: ["gen-status"], queryFn: () => api<{ configured: boolean; model: string }>("/generations/status") });

export const useGenerations = () => useQuery({ queryKey: ["generations"], queryFn: () => api<Generation[]>("/generations") });

export function useGenerate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { prompt: string; albumId?: number | null }) =>
      api<Generation & { image: ImageInfo }>("/generations", {
        method: "POST", body: JSON.stringify({ prompt: b.prompt, consent: true, album_id: b.albumId ?? null }),
      }),
    onSettled: () => ["generations", "images", "albums"].forEach((k) => qc.invalidateQueries({ queryKey: [k] })),
  });
}
