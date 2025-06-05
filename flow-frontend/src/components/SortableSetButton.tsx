import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface SortableSetButtonProps {
  setNumber: number;
  isCompleted: boolean;
  isActive: boolean;
  onSelect: (setNumber: number) => void;
  onRemove: (setNumber: number) => void;
  canRemove: boolean;
  readOnly: boolean;
}

const SortableSetButton: React.FC<SortableSetButtonProps> = ({
  setNumber,
  isCompleted,
  isActive,
  onSelect,
  onRemove,
  canRemove,
  readOnly,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: setNumber,
    disabled: readOnly,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="relative group"
      {...attributes}
      {...listeners}
    >
      <button
        onClick={() => onSelect(setNumber)}
        disabled={readOnly}
        className={`w-12 h-12 rounded-full flex items-center justify-center font-medium cursor-pointer ${
          isCompleted
            ? 'bg-green-100 text-green-800 border-2 border-green-300'
            : isActive
              ? 'bg-blue-100 text-blue-800 border-2 border-blue-500'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
        } ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
      >
        {setNumber}
      </button>
      
      {/* Remove button - appears on hover */}
      {!readOnly && canRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove(setNumber);
          }}
          className="absolute -top-2 -right-2 bg-red-100 text-red-600 rounded-full p-1 hidden group-hover:block hover:bg-red-200"
          title="Remove set"
        >
          <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </div>
  );
};

export default SortableSetButton;