import React, { useCallback, useRef } from 'react';
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

// Custom debounce hook for performance optimization
const useDebounce = (callback: (...args: any[]) => void, delay: number) => {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const debouncedCallback = useCallback((...args: any[]) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]);
  
  // Cleanup function to cancel pending calls
  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);
  
  return { debouncedCallback, cancel };
};

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
      <td className="px-1 py-2 text-center w-6">
        <div
          {...attributes}
          {...listeners}
          className={`cursor-grab active:cursor-grabbing p-1 rounded hover:bg-gray-200 transition-colors ${
            props.readOnly ? 'cursor-not-allowed opacity-50' : ''
          }`}
          title={props.readOnly ? 'Cannot reorder' : 'Drag to reorder'}
        >
          <svg className="w-3 h-3 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="6" r="2"/>
            <circle cx="12" cy="12" r="2"/>
            <circle cx="12" cy="18" r="2"/>
          </svg>
        </div>
      </td>

      {/* Always-Visible Input Content */}
      <InlineSetRowContent {...props} />
    </tr>
  );
};

// Enhanced content component with always-visible inputs and debounced performance
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

  const parseNumber = (value: string, fallback: number, min?: number, max?: number): number => {
    if (!value || value.trim() === '') return fallback;
    const num = parseFloat(value);
    if (isNaN(num)) return fallback;
    if (min !== undefined && num < min) return min;
    if (max !== undefined && num > max) return max;
    return num;
  };

  const commitSetData = async (updatedData: Partial<typeof displayData>) => {
    const newData = { ...displayData, ...updatedData };
    setDisplayData(newData);
    setError(null);

    // Only save if this set has been interacted with (has existing data or user made changes)
    if (existingData || Object.keys(updatedData).length > 0) {
      try {
        setIsSaving(true);
        
        await import('../services/api').then(({ trackExerciseSet }) =>
          trackExerciseSet(exerciseId, setNumber, {
            reps: newData.reps,
            weight: newData.weight,
            rpe: newData.rpe || undefined,
            completed: existingData?.completed || false,
            notes: newData.notes || undefined,
          })
        );
        
        onSetUpdated();
        
      } catch (err) {
        console.error('Error persisting set changes:', err);
        setError('Failed to save changes');
        
        // Revert value on error
        setDisplayData(displayData);
        
        // Retry after brief delay
        setTimeout(() => {
          commitSetData(updatedData);
        }, 1000);
        
      } finally {
        setIsSaving(false);
      }
    }
  };

  // Debounced commit functions for real-time performance
  const debouncedCommitWeight = useDebounce((weight: number) => {
    commitSetData({ weight });
  }, 150); // 150ms debounce for optimal balance

  const debouncedCommitReps = useDebounce((reps: number) => {
    commitSetData({ reps });
  }, 150);

  const debouncedCommitRpe = useDebounce((rpe: number | undefined) => {
    commitSetData({ rpe });
  }, 150);

  // Individual field change handlers with debounced performance optimization
  const handleWeightChange = (value: string) => {
    const weight = parseNumber(value, displayData.weight, 0);
    setDisplayData(prev => ({ ...prev, weight }));
    
    // Debounced API call for real-time persistence
    debouncedCommitWeight.debouncedCallback(weight);
  };

  const handleWeightBlur = () => {
    // Cancel pending debounced call and commit immediately for data integrity
    debouncedCommitWeight.cancel();
    commitSetData({ weight: displayData.weight });
  };

  const handleRepsChange = (value: string) => {
    const reps = parseNumber(value, displayData.reps, 1);
    setDisplayData(prev => ({ ...prev, reps }));
    
    // Debounced API call for real-time persistence
    debouncedCommitReps.debouncedCallback(reps);
  };

  const handleRepsBlur = () => {
    // Cancel pending debounced call and commit immediately for data integrity
    debouncedCommitReps.cancel();
    commitSetData({ reps: displayData.reps });
  };

  const handleRpeChange = (value: string) => {
    const rpe = value.trim() ? parseNumber(value, displayData.rpe || 0, 0, 10) : undefined;
    setDisplayData(prev => ({ ...prev, rpe }));
    
    // Debounced API call for real-time persistence
    debouncedCommitRpe.debouncedCallback(rpe);
  };

  const handleRpeBlur = () => {
    // Cancel pending debounced call and commit immediately for data integrity
    debouncedCommitRpe.cancel();
    commitSetData({ rpe: displayData.rpe });
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
      <td className="px-2 py-2 text-center font-medium w-16">
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

      {/* Weight - Always visible input with debounced performance */}
      <td className="px-1 py-2 w-16">
        <input
          type="text"
          value={displayData.weight}
          onChange={(e) => handleWeightChange(e.target.value)}
          onBlur={handleWeightBlur}
          onFocus={(e) => e.target.select()}
          className={`w-12 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block`}
                        disabled={readOnly}
          placeholder={`${plannedWeight}`}
        />
      </td>

      {/* Reps - Always visible input with debounced performance */}
      <td className="px-1 py-2 w-12">
        <input
          type="text"
          value={displayData.reps}
          onChange={(e) => handleRepsChange(e.target.value)}
          onBlur={handleRepsBlur}
          onFocus={(e) => e.target.select()}
          className={`w-10 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block`}
          disabled={readOnly}
          placeholder={`${plannedReps}`}
        />
      </td>

      {/* RPE - Always visible input with debounced performance */}
      <td className="px-1 py-2 w-12">
        <input
          type="text"
          value={displayData.rpe || ''}
          onChange={(e) => handleRpeChange(e.target.value)}
          onBlur={handleRpeBlur}
          onFocus={(e) => e.target.select()}
          className={`w-10 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block`}
          placeholder="RPE"
          disabled={readOnly}
        />
      </td>

      {/* Notes */}
      <td className="px-2 py-2 w-16">
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
                    const newNotes = notesRef.current.value;
                    setDisplayData(prev => ({ ...prev, notes: newNotes }));
                    commitSetData({ notes: newNotes });
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
      <td className="px-1 py-2 text-center w-16">
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