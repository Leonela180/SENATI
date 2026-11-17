import { Camera, Leaf, Mountain, Sparkles } from "lucide-react";
import { useAppearance } from "@/lib/appearance";
import { cn } from "@/lib/utils";

export function UserAvatar({ name, large = false }: { name: string; large?: boolean }) {
  const { avatar } = useAppearance();
  const Icon = { camera: Camera, leaf: Leaf, mountain: Mountain, spark: Sparkles }[avatar as "camera" | "leaf" | "mountain" | "spark"];
  return <span role="img" aria-label={`Avatar de ${name}`} className={cn("grid shrink-0 place-items-center rounded-2xl bg-brand-soft font-semibold text-brand-strong", large ? "size-20 text-2xl" : "size-9 text-sm")}>
    {Icon ? <Icon className={large ? "size-9" : "size-5"} aria-hidden /> : name.trim().split(/\s+/).slice(0, 2).map(word => word.charAt(0)).join("").toUpperCase() || "?"}
  </span>;
}
