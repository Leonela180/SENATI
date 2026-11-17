import { useState } from "react";
import { toast } from "sonner";
import { KeyRound, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/PageHeader";
import { useChangePassword, useMe, useUpdateProfile } from "@/features/auth/useAuth";
import { ACCENTS, AVATARS, updateAppearance, useAppearance } from "@/lib/appearance";
import { UserAvatar } from "@/components/UserAvatar";

function Section({ icon: Icon, title, description, children }: { icon: typeof UserRound; title: string; description: string; children: React.ReactNode }) {
  return (
    <section className="grid gap-6 rounded-3xl border bg-card p-6 shadow-sm md:grid-cols-[16rem_minmax(0,1fr)] md:p-8">
      <div className="space-y-2">
        <span className="grid size-10 place-items-center rounded-2xl bg-brand-soft text-brand-strong"><Icon className="size-5" aria-hidden /></span>
        <h2 className="font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <div className="max-w-md">{children}</div>
    </section>
  );
}

export default function Profile() {
  const { data: me } = useMe();
  const update = useUpdateProfile();
  const change = useChangePassword();
  const [name, setName] = useState(me?.display_name ?? "");
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const appearance = useAppearance();
  function personalize(patch: Parameters<typeof updateAppearance>[0]) {
    if (!updateAppearance(patch)) toast.error("El navegador no permite guardar preferencias. Se aplicarán durante esta sesión.");
  }

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Perfil" title="Tu cuenta" />
      <div className="flex items-center gap-4">
        <UserAvatar name={me?.display_name || "Usuario"} large />
        <div><p className="text-lg font-semibold">{me?.display_name}</p><p className="text-sm text-muted-foreground">{me?.email}{me?.role === "admin" && " · Administrador técnico"}</p></div>
      </div>

      <Section icon={UserRound} title="Tu estilo" description="Personaliza tu espacio. Estas preferencias se guardan en este navegador y no cambian la vista de otros integrantes.">
        <div className="space-y-6">
          <fieldset className="space-y-2"><legend className="mb-2 text-sm font-medium">Apariencia</legend><div className="flex flex-wrap gap-2">{([['light', 'Claro'], ['dark', 'Oscuro'], ['system', 'Sistema']] as const).map(([mode, label]) => <Button key={mode} variant={appearance.mode === mode ? "default" : "outline"} aria-pressed={appearance.mode === mode} onClick={() => personalize({ mode })}>{label}</Button>)}</div></fieldset>
          <fieldset className="space-y-2"><legend className="mb-2 text-sm font-medium">Color de acento</legend><div className="flex flex-wrap gap-2">{Object.entries(ACCENTS).map(([accent, label]) => <Button key={accent} variant={appearance.accent === accent ? "default" : "outline"} aria-pressed={appearance.accent === accent} onClick={() => personalize({ accent: accent as keyof typeof ACCENTS })}>{label}</Button>)}</div></fieldset>
          <fieldset className="space-y-2"><legend className="mb-2 text-sm font-medium">Avatar</legend><div className="flex flex-wrap gap-2">{Object.entries(AVATARS).map(([avatar, label]) => <Button key={avatar} variant={appearance.avatar === avatar ? "default" : "outline"} aria-pressed={appearance.avatar === avatar} onClick={() => personalize({ avatar: avatar as keyof typeof AVATARS })}>{label}</Button>)}</div></fieldset>
          <label className="flex items-center gap-3 text-sm"><input type="checkbox" checked={appearance.compact} onChange={e => personalize({ compact: e.target.checked })} className="size-4" />Navegación compacta en escritorio</label>
          <Button variant="ghost" onClick={() => personalize({ mode: "dark", accent: "violet", avatar: "initials", compact: false })}>Restablecer apariencia</Button>
        </div>
      </Section>
      <Section icon={UserRound} title="Datos personales" description="El nombre visible aparece en tu panel y para tu equipo.">
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); update.mutate(name, { onSuccess: () => toast.success("Perfil actualizado") }); }}>
          <div className="space-y-2"><Label htmlFor="name">Nombre visible</Label>
            <Input id="name" required maxLength={120} className="h-11" value={name} onChange={(e) => setName(e.target.value)} /></div>
          {update.error && <p role="alert" className="text-sm text-destructive">{(update.error as Error).message}</p>}
          <Button type="submit" className="rounded-xl" disabled={update.isPending || name.trim() === me?.display_name}>Guardar cambios</Button>
        </form>
      </Section>

      <Section icon={KeyRound} title="Contraseña" description="Usa al menos 12 caracteres. Se guarda cifrada con Argon2id.">
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); change.mutate(pw, { onSuccess: () => { toast.success("Contraseña cambiada"); setPw({ current_password: "", new_password: "" }); } }); }}>
          <div className="space-y-2"><Label htmlFor="cur">Contraseña actual</Label>
            <Input id="cur" type="password" autoComplete="current-password" required className="h-11" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} /></div>
          <div className="space-y-2"><Label htmlFor="new">Nueva contraseña</Label>
            <Input id="new" type="password" autoComplete="new-password" required minLength={12} className="h-11" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} /></div>
          {change.error && <p role="alert" className="text-sm text-destructive">{(change.error as Error).message}</p>}
          <Button type="submit" className="rounded-xl" disabled={change.isPending}>Cambiar contraseña</Button>
        </form>
      </Section>
    </div>
  );
}
