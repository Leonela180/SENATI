import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useMe } from "@/features/auth/useAuth";
import { useAcceptInvite } from "@/features/teams/useTeams";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/brand/Logo";

export default function Invitation() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const nav = useNavigate();
  const { data: me } = useMe();
  const accept = useAcceptInvite();
  const { data, isPending, error } = useQuery({ queryKey: ["invitation", token], retry: false,
    queryFn: () => api<{ team_name: string; email: string | null; display_name: string | null }>("/invitations/preview", { method: "POST", body: JSON.stringify({ token }) }) });
  const from = `/app/equipo?token=${encodeURIComponent(token)}`;
  return <main className="grid min-h-screen place-items-center bg-background p-5 text-foreground"><div className="w-full max-w-lg space-y-6 rounded-3xl border bg-card p-8 shadow-sm"><Logo />
    <h1 className="font-display text-3xl font-semibold">Tu equipo te espera</h1>
    {isPending ? <p role="status">Comprobando invitación…</p> : error ? <p role="alert">{(error as Error).message}</p> : data && <>
      <p>Te invitaron a <strong>{data.team_name}</strong> en LUMIA AI.</p>
      {data.email && <p className="break-all text-sm text-muted-foreground">Invitación para {data.email}. Utiliza ese correo para entrar.</p>}
      {me ? <Button disabled={accept.isPending} onClick={() => accept.mutate(token, { onSuccess: () => nav("/app/equipo", { replace: true }) })}>Aceptar invitación</Button> : <div className="flex flex-wrap gap-3"><Button asChild><Link to="/registro" state={{ from, email: data.email || "", display_name: data.display_name || "" }}>Crear mi cuenta</Link></Button><Button asChild variant="outline"><Link to="/login" state={{ from }}>Ya tengo cuenta</Link></Button></div>}
      {accept.error && <p role="alert" className="text-sm text-destructive">{(accept.error as Error).message}</p>}
      <p className="text-xs text-muted-foreground">Tu contraseña la eliges tú. El enlace vence en 72 horas y solo puede utilizarse una vez.</p>
    </>}
  </div></main>;
}
