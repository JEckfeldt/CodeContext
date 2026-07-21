import { cn } from "@/lib/cn";
import type { HTMLAttributes } from "react";

type BadgeVariant = "default" | "primary" | "secondary" | "outline";

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-border-subtle text-muted",
  primary: "bg-primary-muted text-[#1d4ed8]",
  secondary: "bg-accent-purple-muted text-[#6d28d9]",
  outline: "border border-border bg-surface text-muted",
};

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  variant?: BadgeVariant;
};

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
        variantStyles[variant],
        className,
      )}
      {...props}
    />
  );
}
