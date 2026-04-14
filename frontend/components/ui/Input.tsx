import { InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, hint, error, className = "", ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-medium uppercase tracking-widest text-ash">
          {label}
        </label>
        <input
          ref={ref}
          className={`
            w-full bg-surface-raised border rounded-xl px-4 py-3
            font-body text-sm text-white placeholder:text-ash-dark
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent/40
            ${error ? "border-red-500/60" : "border-border hover:border-border-strong"}
            ${className}
          `}
          {...props}
        />
        {hint && !error && (
          <p className="text-xs text-ash-dark">{hint}</p>
        )}
        {error && (
          <p className="text-xs text-red-400">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";