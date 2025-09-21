import type * as React from "react"
import { cn } from "@/lib/utils"

interface BadgeProps extends React.ComponentProps<"span"> {
  variant?: "default" | "konnect" | "verified" | "outline"
}

const Badge=({ className, variant = "default", ...props }: BadgeProps)=> {
  const baseClasses =
    "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap"

  const variantClasses = {
    default: "border-transparent bg-primary text-primary-foreground",
    konnect: "border-transparent bg-[#00ff88] text-black font-semibold",
    verified: "border-[#00ff88]/30 bg-[#00ff88]/20 text-[#00ff88]",
    outline: "border-border bg-transparent text-foreground",
  }

  return <span className={cn(baseClasses, variantClasses[variant], className)} {...props} />
}


export default Badge
