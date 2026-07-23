import {forwardRef,InputHTMLAttributes} from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement>{
    label?:string,
    error?:string
}

const Input=forwardRef<HTMLInputElement,InputProps>(
    ({label,error,className="", ...props}, ref)=>{return(
<div className="space-y-3">
{label && (<label className="block text-sm font-medium">
    {label}
</label>)}
 <input
          ref={ref}
          {...props}
          className={`
            w-full
            rounded-lg
            border
            border-gray-300
            px-4
            py-3
            outline-none
            transition
            focus:border-orange-500
            focus:ring-2
            focus:ring-orange-300
            ${error ? "border-red-500" : ""}
            ${className}
          `}
        />
        {error && (
          <p className="text-sm text-red-500">
            {error}
          </p>
        )}
</div>
    )}
)

Input.displayName = "Input";

export default Input;