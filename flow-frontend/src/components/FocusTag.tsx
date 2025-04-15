import React from 'react';

type FocusType = 'squat' | 'bench' | 'deadlift' | 'cardio' | 'rest' | string;

interface FocusTagProps {
  focus: FocusType;
  size?: 'sm' | 'md' | 'lg';
}

const FocusTag: React.FC<FocusTagProps> = ({ focus, size = 'md' }) => {
  const getTagColor = (focusType: string): string => {
    switch (focusType.toLowerCase()) {
      case 'squat':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'bench':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'deadlift':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'cardio':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'rest':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  };

  return (
    <span className={`inline-flex items-center font-medium rounded-full border ${getTagColor(focus)} ${sizeClasses[size]}`}>
      {focus ? focus.charAt(0).toUpperCase() + focus.slice(1) : 'None'}
    </span>
  );
};

export default FocusTag;