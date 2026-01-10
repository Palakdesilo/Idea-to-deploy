import React from 'react';
import clsx from 'clsx';

/**
 * @typedef {'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'} ButtonVariant
 * @typedef {'sm' | 'md' | 'lg'} ButtonSize
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * The visual style variant of the button.
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  /**
   * The size of the button.
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * If true, the button will show a loading spinner and be disabled.
   * @default false
   */
  loading?: boolean;
  /**
   * If true, the button will be disabled.
   * @default false
   */
  disabled?: boolean;
  /**
   * The content of the button. Can be text, icons, or any React node.
   */
  children: React.ReactNode;
  /**
   * Optional CSS class names to apply to the button for custom styling.
   */
  className?: string;
  /**
   * An accessible label for the button, especially useful for icon-only buttons.
   */
  'aria-label'?: string;
}

/**
 * A reusable Button component with various styles, sizes, loading states, and accessibility features.
 *
 * @param {ButtonProps} props - The props for the Button component.
 * @returns {JSX.Element} The rendered button element.
 */
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled: propDisabled = false, // Rename to avoid conflict with native 'disabled'
  children,
  className,
  'aria-label': ariaLabel,
  ...rest
}) => {
  const isDisabled = propDisabled || loading;

  const baseStyles = 'font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-2.5 text-lg',
  };

  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400',
    outline: 'border border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500',
    ghost: 'text-blue-600 hover:bg-blue-50 focus:ring-blue-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };

  const disabledStyles = 'opacity-50 cursor-not-allowed';
  const loadingContentStyles = 'flex items-center justify-center gap-2'; // For spacing between spinner and text

  const buttonClasses = clsx(
    baseStyles,
    sizeStyles[size],
    variantStyles[variant],
    isDisabled && disabledStyles,
    loading && loadingContentStyles, // Apply flex styles when loading to center spinner and text
    className // Allow custom classes to override or extend
  );

  // Simple SVG spinner for demonstration. In a real project, consider using a library like 'react-icons'.
  const Spinner = (
    <svg
      className="animate-spin h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      ></circle>
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
  );

  // Adjust spinner color based on button variant for better contrast
  const spinnerColorClass = variant === 'primary' || variant === 'danger' ? 'text-white' : 'text-gray-600';
  const styledSpinner = React.cloneElement(Spinner, {
    className: clsx(Spinner.props.className, spinnerColorClass),
  });

  return (
    <button
      className={buttonClasses}
      disabled={isDisabled}
      aria-disabled={isDisabled} // Explicit aria-disabled for semantic clarity
      aria-label={ariaLabel || (typeof children === 'string' ? children : undefined)} // Use children as label if string and no explicit aria-label
      {...rest}
    >
      {loading && styledSpinner}
      {children}
    </button>
  );
};

export default Button;