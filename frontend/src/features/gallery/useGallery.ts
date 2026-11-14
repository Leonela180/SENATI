import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Album, ImageInfo, ImagePage } from "@/lib/types";

export const useAlbums = () => useQuery({ queryKey: ["albums"], queryFn: () => api<Album[]>("/albums") });

export const useImages = (album: string, q: string, page: number) =>
  useQuery({
    queryKey: ["images", album, q, page],
    queryFn: () => api<ImagePage>(`/images?page=${page}${album ? `&album=${album}` : ""}${q ? `&q=${encodeURIComponent(q)}` : ""}`),
  });

export const useImage = (id: number | null) =>
  useQuery({ queryKey: ["image", id], queryFn: () => api<ImageInfo>(`/images/${id}`), enabled: !!id });

function useInvalidate() {
  const qc = useQueryClient();
  return () => ["images", "albums", "image"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
}

export function useUploadToGallery() {
  const inv = useInvalidate();
  return useMutation({
    mutationFn: (b: { file: File; albumId?: number | null }) => {
      const fd = new FormData();
      fd.append("file", b.file);
      fd.append("declaracion_ia", "true");
      if (b.albumId) fd.append("album_id", String(b.albumId));
      return api<ImageInfo>("/images", { method: "POST", body: fd });
    },
    onSuccess: inv,
  });
}

export function useCreateAlbum() {
  const inv = useInvalidate();
  return useMutation({ mutationFn: (name: string) => api<Album>("/albums", { method: "POST", body: JSON.stringify({ name }) }), onSuccess: inv });
}

export function useDeleteAlbum() {
  const inv = useInvalidate();
  return useMutation({ mutationFn: (id: number) => api(`/albums/${id}`, { method: "DELETE" }), onSuccess: inv });
}

export function useMoveImage() {
  const inv = useInvalidate();
  return useMutation({
    mutationFn: (b: { id: number; albumId: number | null }) =>
      api<ImageInfo>(`/images/${b.id}/album`, { method: "PATCH", body: JSON.stringify({ album_id: b.albumId }) }),
    onSuccess: inv,
  });
}

export function useDeleteImage() {
  const inv = useInvalidate();
  return useMutation({ mutationFn: (id: number) => api(`/images/${id}`, { method: "DELETE" }), onSuccess: inv });
}

export function useSaveResult() {
  const inv = useInvalidate();
  return useMutation({ mutationFn: (jobId: number) => api<ImageInfo>(`/jobs/${jobId}/save`, { method: "POST" }), onSuccess: inv });
}
