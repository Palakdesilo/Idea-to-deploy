import React, { InputHTMLAttributes, forwardRef, createContext, useContext } from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

const RadioGroupContext = createContext<any>(null);

const RadioGroup = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & { value?: string, onValueChange?: (value: string) => void }>(
    ({ className, value, onValueChange, ...props }, ref) => {
        return (
            <RadioGroupContext.Provider value={{ value, onValueChange }}>
                <div className={cn("grid gap-2", className)} ref={ref} {...props} />
            </RadioGroupContext.Provider>
        );
    }
);
RadioGroup.displayName = "RadioGroup";

const RadioGroupItem = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & { value: string }>(
    ({ className, value, ...props }, ref) => {
        const context = useContext(RadioGroupContext);
        const checked = context?.value === value;

        return (
            <div className="flex items-center space-x-2">
                <input
                    type="radio"
                    ref={ref}
                    className={cn(
                        "aspect-square h-4 w-4 rounded-full border border-primary text-primary shadow focus:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
                        className
                    )}
                    checked={checked}
                    onChange={() => context?.onValueChange?.(value)}
                    value={value}
                    {...props}
                />
            </div>
        );
    }
);
RadioGroupItem.displayName = "RadioGroupItem";

export { RadioGroup, RadioGroupItem };
