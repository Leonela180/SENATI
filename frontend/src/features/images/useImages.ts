import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ImageInfo } from "@/lib/types";

export const useUploadImage = () =>
  useMutation({
    mutationFn: (file: File) => {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("declaracion_ia", "true");
      return api<ImageInfo>("/images", { method: "POST", body: fd });
    },
  });

export function useSetVisibility() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { imageId: number; visibility: "private" | "team" }) =>
      api<ImageInfo>(`/images/${b.imageId}/visibility`, { method: "PATCH", body: JSON.stringify({ visibility: b.visibility }) }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["job"] }); qc.invalidateQueries({ queryKey: ["jobs"] }); },
  });
}
