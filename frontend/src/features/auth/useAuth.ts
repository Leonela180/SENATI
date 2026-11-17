import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, resetCsrf } from "@/lib/api";
import type { User } from "@/lib/types";

export const useMe = () =>
  useQuery({ queryKey: ["me"], queryFn: () => api<User>("/auth/me"), retry: false, staleTime: 60_000 });

export function useLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { email: string; password: string }) => api<User>("/auth/login", { method: "POST", body: JSON.stringify(b) }),
    onSuccess: (u) => { resetCsrf(); qc.setQueryData(["me"], u); },
  });
}

export function useRegister() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { email: string; display_name: string; password: string }) =>
      api<User>("/auth/register", { method: "POST", body: JSON.stringify(b) }),
    onSuccess: (u) => { resetCsrf(); qc.setQueryData(["me"], u); },
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api("/auth/logout", { method: "POST" }),
    onSuccess: () => { resetCsrf(); qc.clear(); },
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (display_name: string) => api<User>("/users/me", { method: "PATCH", body: JSON.stringify({ display_name }) }),
    onSuccess: (u) => qc.setQueryData(["me"], u),
  });
}

export const useChangePassword = () =>
  useMutation({
    mutationFn: (b: { current_password: string; new_password: string }) =>
      api("/users/me/change-password", { method: "POST", body: JSON.stringify(b) }),
  });
