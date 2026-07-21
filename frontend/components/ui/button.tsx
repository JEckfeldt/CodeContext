import { cn } from "@/lib/cn";
import type { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "brand" | "ghost" | "outline";
type ButtonSize = "sm" | "md" | "lg";

const variantStyles: Record<ButtonVariant, string> = {
  brand:
    "bg-[linear-gradient(135deg,#2563eb_0%,#7c3aed_100%)] text-white shadow-sm hover:brightness-105 focus-visible:ring-accent-purple/30",
  primary:
    "bg-primary text-primary-foreground shadow-sm hover:bg-[#1d4ed8] focus-visible:ring-primary/30",
  secondary:
    "border border-[color-mix(in_srgb,var(--accent-purple)_22%,var(--border))] bg-accent-purple-muted text-[#5b21b6] hover:bg-[#ddd6fe] focus-visible:ring-accent-purple/25",
  ghost:
    "text-foreground hover:bg-border-subtle focus-visible:ring-primary/20",
  outline:
    "border border-border bg-surface text-foreground hover:border-[color-mix(in_srgb,var(--primary)_28%,var(--border))] hover:bg-primary-muted/40 focus-visible:ring-primary/20",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "h-8 px-3 text-xs",
  md: "h-9 px-4 text-sm",
  lg: "h-10 px-5 text-sm",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function Button({
  className,
  variant = "primary",
  size = "md",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
        variantStyles[variant],
        sizeStyles[size],
        className,
      )}
      {...props}
    />
  );
}
