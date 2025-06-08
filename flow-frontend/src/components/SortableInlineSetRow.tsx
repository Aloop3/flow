import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { ExerciseSetData } from '../services/api';

interface SortableInlineSetRowProps {
  exerciseId: string;
  setNumber: number;
  existingData?: ExerciseSetData;
  previousSetData?: ExerciseSetData;
  plannedReps: number;
  plannedWeight: number;
  readOnly?: boolean;
  onSetUpdated: () => void;
}

const SortableInlineSetRow: React.FC<SortableInlineSetRowProps> = (props) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: props.setNumber,
    disabled: props.readOnly,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 1000 : 'auto',
  };

  return (
    <tr
      ref={setNodeRef}
      style={style}
      className={`border-b hover:bg-gray-50 ${isDragging ? 'opacity-75 bg-blue-50' : ''}`}
    >
      {/* Drag Handle Column */}
      <td className="px-2 py-3 text-center w-8">
        <div
          {...attributes}
          {...listeners}
          className={`cursor-grab active:cursor-grabbing p-1 rounded hover:bg-gray-200 transition-colors ${
            props.readOnly ? 'cursor-not-allowed opacity-50' : ''
          }`}
          title={props.readOnly ? 'Cannot reorder' : 'Drag to reorder'}
        >
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
          </svg>
        </div>
      </td>

      {/* Inline Set Row Content */}
      <InlineSetRowContent {...props} />
    </tr>
  );
};

// Extract the content part of InlineSetRow (without the <tr> wrapper)
const InlineSetRowContent: React.FC<SortableInlineSetRowProps> = ({
  exerciseId,
  setNumber,
  existingData,
  previousSetData,
  plannedReps,
  plannedWeight,
  readOnly = false,
  onSetUpdated,
}) => {
  // Copy all the logic from InlineSetRow.tsx but render only the <td> elements
  const [isEditing, setIsEditing] = React.useState(false);
  const [isSaving, setIsSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [notesExpanded, setNotesExpanded] = React.useState(false);
  
  // Local state for form data
  const [formData, setFormData] = React.useState<{
    reps: number;
    weight: number;
    rpe: number | undefined;
    notes: string;
  }>({
    reps: existingData?.reps ?? plannedReps,
    weight: existingData?.weight ?? plannedWeight,
    rpe: existingData?.rpe ?? undefined,
    notes: existingData?.notes ?? '',
  });

  // Refs for auto-focus management
  const repsRef = React.useRef<HTMLInputElement>(null);
  const weightRef = React.useRef<HTMLInputElement>(null);
  const rpeRef = React.useRef<HTMLInputElement>(null);
  const notesRef = React.useRef<HTMLTextAreaElement>(null);

  // Auto-populate from previous set when creating new set
  React.useEffect(() => {
    if (!existingData && previousSetData) {
      setFormData({
        reps: previousSetData.reps,
        weight: previousSetData.weight,
        rpe: previousSetData.rpe,
        notes: '', // Don't copy notes from previous set
      });
    }
  }, [existingData, previousSetData]);

  const isCompleted = existingData?.completed ?? false;

  // Copy all the handler functions from InlineSetRow.tsx
  const handleInputChange = (field: keyof typeof formData, value: string | number | undefined) => {
    // Handle empty string inputs for numeric fields
    if (field === 'reps' || field === 'weight') {
      if (value === '' || value === null) {
        setFormData(prev => ({
          ...prev,
          [field]: field === 'reps' ? 1 : 0, // reps defaults to 1, weight to 0
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          [field]: Number(value),
        }));
      }
    } else if (field === 'rpe') {
      if (value === '' || value === null) {
        setFormData(prev => ({
          ...prev,
          rpe: undefined,
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          rpe: Number(value),
        }));
      }
    } else if (field === 'notes') {
      setFormData(prev => ({
        ...prev,
        notes: String(value || ''),
      }));
    }
    setError(null);
  };

  const validateData = () => {
    if (formData.reps <= 0) {
      throw new Error('Reps must be greater than zero');
    }
    if (formData.weight < 0) {
      throw new Error('Weight cannot be negative');
    }
    if (formData.rpe !== undefined && (formData.rpe < 0 || formData.rpe > 10)) {
      throw new Error('RPE must be between 0 and 10');
    }
  };

  const handleToggleCompletion = async () => {
    if (readOnly || isSaving) return;
    
    try {
      setIsSaving(true);
      setError(null);

      if (isCompleted) {
        // Mark as incomplete
        await import('../services/api').then(({ trackExerciseSet }) =>
          trackExerciseSet(exerciseId, setNumber, {
            reps: formData.reps,
            weight: formData.weight,
            rpe: formData.rpe || undefined,
            completed: false,
            notes: formData.notes || undefined,
          })
        );
      } else {
        // Mark as complete - validate data first
        validateData();
        await import('../services/api').then(({ trackExerciseSet }) =>
          trackExerciseSet(exerciseId, setNumber, {
            reps: formData.reps,
            weight: formData.weight,
            rpe: formData.rpe || undefined,
            completed: true,
            notes: formData.notes || undefined,
          })
        );
      }

      onSetUpdated();
    } catch (err: any) {
      setError(err.message || 'Failed to update set completion');
      console.error('Error toggling completion:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCellClick = (field: 'reps' | 'weight' | 'rpe') => {
    if (readOnly) return;
    setIsEditing(true);
    
    // Focus appropriate input after state update
    setTimeout(() => {
      if (field === 'reps' && repsRef.current) repsRef.current.focus();
      if (field === 'weight' && weightRef.current) weightRef.current.focus();
      if (field === 'rpe' && rpeRef.current) rpeRef.current.focus();
    }, 0);
  };

  const handleBlur = async (e: React.FocusEvent) => {
    const relatedTarget = e.relatedTarget as HTMLElement;
    const currentRow = e.currentTarget.closest('tr');
    const targetInSameRow = relatedTarget && currentRow?.contains(relatedTarget);
    
    if (targetInSameRow) {
      return;
    }

    setIsEditing(false);
  };

  const toggleNotes = () => {
    setNotesExpanded(!notesExpanded);
    if (!notesExpanded && notesRef.current) {
      setTimeout(() => notesRef.current?.focus(), 0);
    }
  };

  return (
    <>
      {/* Set Number */}
      <td className="px-2 py-3 text-center font-medium w-12">
        <div className="flex items-center justify-center">
          <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            isCompleted 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-600'
          }`}>
            {setNumber}
          </span>
        </div>
      </td>

      {/* Weight */}
      <td className="px-2 py-3 w-20" onClick={() => handleCellClick('weight')}>
        {isEditing ? (
          <input
            ref={weightRef}
            type="number"
            value={formData.weight}
            onChange={(e) => handleInputChange('weight', Number(e.target.value) || 0)}
            onBlur={handleBlur}
            className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            min="0"
            step="0.5"
            disabled={isSaving}
          />
        ) : (
          <div className="px-2 py-1 text-sm cursor-text hover:bg-gray-100 rounded">
            {formData.weight}
          </div>
        )}
      </td>

      {/* Reps */}
      <td className="px-2 py-3 w-16" onClick={() => handleCellClick('reps')}>
        {isEditing ? (
          <input
            ref={repsRef}
            type="number"
            value={formData.reps}
            onChange={(e) => handleInputChange('reps', Number(e.target.value) || 0)}
            onBlur={handleBlur}
            className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            min="1"
            disabled={isSaving}
          />
        ) : (
          <div className="px-2 py-1 text-sm cursor-text hover:bg-gray-100 rounded">
            {formData.reps}
          </div>
        )}
      </td>

      {/* RPE */}
      <td className="px-2 py-3 w-16" onClick={() => handleCellClick('rpe')}>
        {isEditing ? (
          <input
            ref={rpeRef}
            type="number"
            value={formData.rpe || ''}
            onChange={(e) => handleInputChange('rpe', Number(e.target.value) || undefined)}
            onBlur={handleBlur}
            className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            min="0"
            max="10"
            step="0.5"
            placeholder="0-10"
            disabled={isSaving}
          />
        ) : (
          <div className="px-2 py-1 text-sm cursor-text hover:bg-gray-100 rounded">
            {formData.rpe || '-'}
          </div>
        )}
      </td>

      {/* Notes */}
      <td className="px-2 py-3 w-16">
        <button
          onClick={toggleNotes}
          className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
            formData.notes 
              ? 'bg-blue-100 text-blue-600' 
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
          }`}
          title={formData.notes ? 'View notes' : 'Add notes'}
          disabled={readOnly}
        >
          📝
        </button>
        {notesExpanded && (
          <div className="absolute z-10 mt-1 p-2 bg-white border border-gray-300 rounded-lg shadow-lg min-w-48">
            <textarea
              ref={notesRef}
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              onBlur={handleBlur}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              rows={3}
              placeholder="Notes for this set..."
              disabled={readOnly || isSaving}
            />
            <div className="flex justify-end mt-2 space-x-2">
              <button
                onClick={() => setNotesExpanded(false)}
                className="px-2 py-1 text-xs text-gray-600 hover:text-gray-800"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </td>

      {/* Completion Status */}
      <td className="px-2 py-3 text-center w-12">
        {isSaving ? (
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        ) : (
          <button
            onClick={handleToggleCompletion}
            disabled={readOnly}
            className={`w-6 h-6 rounded-full flex items-center justify-center mx-auto transition-all duration-200 ${
              readOnly 
                ? 'cursor-not-allowed opacity-50' 
                : 'cursor-pointer hover:scale-110 transform'
            } ${
              isCompleted
                ? 'bg-green-500 text-white hover:bg-green-600 shadow-md'
                : 'border-2 border-gray-300 hover:border-green-400 hover:bg-green-50'
            }`}
            title={isCompleted ? 'Mark incomplete' : 'Mark complete'}
          >
            {isCompleted && (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>
        )}
      </td>

      {/* Error display */}
      {error && (
        <td colSpan={7} className="px-2 py-1">
          <div className="text-xs text-red-600 bg-red-50 rounded px-2 py-1">
            {error}
          </div>
        </td>
      )}
    </>
  );
};

export default SortableInlineSetRow;