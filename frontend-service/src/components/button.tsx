import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
}

export default function CButton({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const variants = {
    primary:
      "bg-orange-600 text-white hover:bg-orange-700",

    secondary:
      "bg-gray-200 text-gray-800 hover:bg-gray-300",

    outline:
      "border border-orange-600 text-blue-600 hover:bg-orange-50",

    danger:
      "bg-red-600 text-white hover:bg-red-700",
  };

  const sizes = {
    sm: "px-3 py-2 text-sm",
    md: "px-5 py-3",
    lg: "px-6 py-4 text-lg",
  };

  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={`
        inline-flex
        items-center
        justify-center
        rounded-lg
        font-medium
        transition
        duration-200
        disabled:opacity-50
        disabled:cursor-not-allowed
        focus:ring-2
        focus:ring-blue-400
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
    >
      {loading ? "Loading..." : children}
    </button>
  );
}