import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", loading = false, children, className = "", disabled, ...props }, ref) => {
    const base =
      "inline-flex items-center justify-center gap-2 font-body font-medium text-sm rounded-xl transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 disabled:pointer-events-none disabled:opacity-40 select-none";

    const variants = {
      primary:
        "bg-accent text-ink px-6 py-3 hover:bg-accent-dim active:scale-[0.98] shadow-[0_0_32px_rgba(232,255,71,0.25)] hover:shadow-[0_0_48px_rgba(232,255,71,0.4)]",
      ghost:
        "bg-transparent border border-border text-ash-light px-5 py-2.5 hover:border-border-strong hover:text-white",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`${base} ${variants[variant]} ${className}`}
        {...props}
      >
        {loading && (
          <svg
            className="w-4 h-4 animate-spin"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
          >
            <circle cx="12" cy="12" r="10" strokeOpacity={0.25} />
            <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";