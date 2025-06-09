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

// Simplified content component with uncontrolled inputs
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
  const [isEditing, setIsEditing] = React.useState(false);
  const [isSaving, setIsSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [notesExpanded, setNotesExpanded] = React.useState(false);
  
  // Single state for display values
  const [displayData, setDisplayData] = React.useState<{
    reps: number;
    weight: number;
    rpe: number | undefined;
    notes: string;
  }>({
    reps: existingData?.reps ?? previousSetData?.reps ?? plannedReps,
    weight: existingData?.weight ?? previousSetData?.weight ?? plannedWeight,
    rpe: existingData?.rpe ?? previousSetData?.rpe ?? undefined,
    notes: existingData?.notes ?? '',
  });

  // Refs for uncontrolled inputs
  const repsRef = React.useRef<HTMLInputElement>(null);
  const weightRef = React.useRef<HTMLInputElement>(null);
  const rpeRef = React.useRef<HTMLInputElement>(null);
  const notesRef = React.useRef<HTMLTextAreaElement>(null);

  const isCompleted = existingData?.completed ?? false;

  // Auto-populate from previous set when creating new set
  React.useEffect(() => {
    if (!existingData && previousSetData) {
      setDisplayData({
        reps: previousSetData.reps,
        weight: previousSetData.weight,
        rpe: previousSetData.rpe,
        notes: '', // Don't copy notes from previous set
      });
    }
  }, [existingData, previousSetData]);

  // Update component state when existingData changes from parent
  React.useEffect(() => {
    if (existingData) {
      setDisplayData({
        reps: existingData.reps,
        weight: existingData.weight,
        rpe: existingData.rpe,
        notes: existingData.notes || '',
      });
    }
  }, [existingData]);

  // Mobile-first: commit on field blur (when tapping to next field)
  const handleInputBlur = () => {
    // Small delay to allow focus to move to next field before committing
    setTimeout(() => {
      // Only commit if focus has moved away from all input fields in this row
      const activeElement = document.activeElement;
      const isStillInInputs = (
        activeElement === repsRef.current ||
        activeElement === weightRef.current ||
        activeElement === rpeRef.current
      );
      
      if (!isStillInInputs && isEditing) {
        commitEditingValues();
      }
    }, 100);
  };

  const parseNumber = (value: string, fallback: number, min?: number, max?: number): number => {
    if (!value || value.trim() === '') return fallback;
    const num = parseFloat(value);
    if (isNaN(num)) return fallback;
    if (min !== undefined && num < min) return min;
    if (max !== undefined && num > max) return max;
    return num;
  };

  const commitEditingValues = async () => {
    if (!isEditing) return;

    const newData = {
      reps: parseNumber(repsRef.current?.value || '', displayData.reps, 1),
      weight: parseNumber(weightRef.current?.value || '', displayData.weight, 0),
      rpe: rpeRef.current?.value?.trim() 
        ? parseNumber(rpeRef.current.value, displayData.rpe || 0, 0, 10) 
        : undefined,
      notes: displayData.notes, // Notes handled separately
    };

    setDisplayData(newData);
    setIsEditing(false);
    setError(null);

    // Persist changes immediately to backend for better mobile UX and sorting
    try {
      await import('../services/api').then(({ trackExerciseSet }) =>
        trackExerciseSet(exerciseId, setNumber, {
          reps: newData.reps,
          weight: newData.weight,
          rpe: newData.rpe || undefined,
          completed: existingData?.completed || false,
          notes: newData.notes || undefined,
        })
      );
      
      // Force refresh of parent component data
      onSetUpdated();
      
      // Additional debug logging to verify the save
      console.log(`Set ${setNumber} updated:`, {
        reps: newData.reps,
        weight: newData.weight,
        rpe: newData.rpe,
        completed: existingData?.completed || false
      });
      
    } catch (err) {
      console.error('Error persisting set changes:', err);
      setError('Failed to save changes. Please try again.');
    }
  };

  const handleCellClick = (field: 'reps' | 'weight' | 'rpe') => {
    if (readOnly || isSaving) return;
    
    setIsEditing(true);
    setError(null);
    
    // Set input values and focus after render
    setTimeout(() => {
      if (field === 'reps' && repsRef.current) {
        repsRef.current.value = String(displayData.reps);
        repsRef.current.focus();
        repsRef.current.select();
      }
      if (field === 'weight' && weightRef.current) {
        weightRef.current.value = String(displayData.weight);
        weightRef.current.focus();
        weightRef.current.select();
      }
      if (field === 'rpe' && rpeRef.current) {
        rpeRef.current.value = displayData.rpe ? String(displayData.rpe) : '';
        rpeRef.current.focus();
        rpeRef.current.select();
      }
    }, 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      commitEditingValues();
    }
    if (e.key === 'Escape') {
      setIsEditing(false);
    }
  };

  const validateData = () => {
    if (displayData.reps <= 0) {
      throw new Error('Reps must be greater than zero');
    }
    if (displayData.weight < 0) {
      throw new Error('Weight cannot be negative');
    }
    if (displayData.rpe !== undefined && (displayData.rpe < 0 || displayData.rpe > 10)) {
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
            reps: displayData.reps,
            weight: displayData.weight,
            rpe: displayData.rpe || undefined,
            completed: false,
            notes: displayData.notes || undefined,
          })
        );
      } else {
        // Mark as complete - validate data first
        validateData();
        await import('../services/api').then(({ trackExerciseSet }) =>
          trackExerciseSet(exerciseId, setNumber, {
            reps: displayData.reps,
            weight: displayData.weight,
            rpe: displayData.rpe || undefined,
            completed: true,
            notes: displayData.notes || undefined,
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

  const toggleNotes = () => {
    setNotesExpanded(!notesExpanded);
    if (!notesExpanded && notesRef.current) {
      setTimeout(() => {
        if (notesRef.current) {
          notesRef.current.value = displayData.notes;
          notesRef.current.focus();
        }
      }, 0);
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
            type="text"
            onKeyDown={handleKeyDown}
            onBlur={handleInputBlur}
            className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            disabled={isSaving}
            placeholder={`${plannedWeight} (planned)`}
          />
        ) : (
          <div className="px-2 py-1 text-sm cursor-text hover:bg-gray-100 rounded">
            {displayData.weight}
          </div>
        )}
      </td>

      {/* Reps */}
      <td className="px-2 py-3 w-16" onClick={() => handleCellClick('reps')}>
        {isEditing ? (
          <input
            ref={repsRef}
            type="text"
            onKeyDown={handleKeyDown}
            onBlur={handleInputBlur}
            className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            disabled={isSaving}
            placeholder={`${plannedReps} (planned)`}
          />
        ) : (
          <div className="px-2 py-1 text-sm cursor-text hover:bg-gray-100 rounded">
            {displayData.reps}
          </div>
        )}
      </td>

      {/* RPE */}
      <td className="px-2 py-3 w-16" onClick={() => handleCellClick('rpe')}>
        {isEditing ? (
          <input
            ref={rpeRef}
            type="text"
            onKeyDown={handleKeyDown}
            onBlur={handleInputBlur}
            className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="Enter RPE"
            disabled={isSaving}
          />
        ) : (
          <div className="px-2 py-1 text-sm cursor-text hover:bg-gray-100 rounded">
            {displayData.rpe || '-'}
          </div>
        )}
      </td>

      {/* Notes */}
      <td className="px-2 py-3 w-16">
        <button
          onClick={toggleNotes}
          className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
            displayData.notes 
              ? 'bg-blue-100 text-blue-600' 
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
          }`}
          title={displayData.notes ? 'View notes' : 'Add notes'}
          disabled={readOnly}
        >
          📝
        </button>
        {notesExpanded && (
          <div className="absolute z-10 mt-1 p-2 bg-white border border-gray-300 rounded-lg shadow-lg min-w-48">
            <textarea
              ref={notesRef}
              onKeyDown={(e) => {
                if (e.key === 'Escape') setNotesExpanded(false);
              }}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              rows={3}
              placeholder="Notes for this set..."
              disabled={readOnly || isSaving}
            />
            <div className="flex justify-end mt-2 space-x-2">
              <button
                onClick={() => {
                  if (notesRef.current) {
                    setDisplayData(prev => ({ ...prev, notes: notesRef.current?.value || '' }));
                  }
                  setNotesExpanded(false);
                }}
                className="px-2 py-1 text-xs text-blue-600 hover:text-blue-800"
              >
                Save
              </button>
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