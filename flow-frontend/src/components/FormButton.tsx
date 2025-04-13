import React, { ReactNode } from 'react';
import LoadingSpinner from './LoadingSpinner';

interface FormButtonProps {
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  children: ReactNode;
  className?: string;
}

const FormButton: React.FC<FormButtonProps> = ({
  type = 'button',
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  onClick,
  children,
  className = '',
}) => {
  // Base styles
  const baseStyles = 'inline-flex justify-center items-center rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  // Size variations
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };
  
  // Variant styles (background, text color, etc)
  const variantClasses = {
    primary: 'border border-transparent bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-300',
    secondary: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-400',
    danger: 'border border-transparent bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-red-300'
  };

  // Combine all classes
  const buttonClasses = `
    ${baseStyles} 
    ${sizeClasses[size]} 
    ${variantClasses[variant]} 
    ${disabled || isLoading ? 'cursor-not-allowed' : ''} 
    ${className}
  `;

  // Spinner size based on button size
  const spinnerSize = size === 'lg' ? 'md' : 'sm';

  return (
    <button
      type={type}
      className={buttonClasses}
      disabled={disabled || isLoading}
      onClick={onClick}
    >
      {isLoading && (
        <LoadingSpinner size={spinnerSize} className="mr-2 -ml-1" />
      )}
      {children}
    </button>
  );
};

export default FormButton;