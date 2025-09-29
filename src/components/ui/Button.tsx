import type * as React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ComponentProps<"button"> {
  variant?: "default" | "konnect" | "outline";
  size?: "default" | "sm" | "lg";
}

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonProps) {
  const baseClasses =
    "inline-flex items-center cursor-pointer justify-center gap-2 whitespace-nowrap rounded-[100px] font-medium transition-all disabled:pointer-events-none disabled:opacity-50";

  const variantClasses = {
    default: "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
    konnect:
      "bg-[#00ff88] text-black shadow-lg hover:bg-[#00ff88]/90 hover:shadow-xl font-semibold",
    outline:
      "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground",
  };

  const sizeClasses = {
    default: "h-9 px-8 py-4 text-sm",
    sm: "h-8 px-3 py-1.5 text-xs",
    lg: "h-11 px-6 py-3 text-base",
  };

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    />
  );
}

export default Button;
