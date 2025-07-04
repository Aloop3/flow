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
  onSetCompletion?: (setNumber: number, completed: boolean) => void;
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
      <td className="px-0.5 md:px-2 py-2 text-center w-4 md:w-8">
        <div
          {...attributes}
          {...listeners}
          className={`cursor-grab active:cursor-grabbing p-0.5 rounded hover:bg-gray-200 transition-colors ${
            props.readOnly ? 'cursor-not-allowed opacity-50' : ''
          }`}
          title={props.readOnly ? 'Cannot reorder' : 'Drag to reorder'}
        >
          <svg className="w-2 h-2 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="6" r="1.5"/>
            <circle cx="12" cy="12" r="1.5"/>
            <circle cx="12" cy="18" r="1.5"/>
          </svg>
        </div>
      </td>

      {/* Always-Visible Input Content */}
      <InlineSetRowContent {...props} />
    </tr>
  );
};

// Enhanced content component with optimistic updates
const InlineSetRowContent: React.FC<SortableInlineSetRowProps> = ({
  exerciseId,
  setNumber,
  existingData,
  previousSetData,
  plannedReps,
  plannedWeight,
  readOnly = false,
  onSetUpdated,
  onSetCompletion,
}) => {
  const [isSaving, setIsSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [notesExpanded, setNotesExpanded] = React.useState(false);

  // Single state for display values including completion status
  const [displayData, setDisplayData] = React.useState<{
    reps: number;
    weight: number;
    rpe: number | undefined;
    notes: string;
    completed: boolean;
  }>({
    reps: existingData?.reps ?? previousSetData?.reps ?? plannedReps,
    weight: existingData?.weight ?? previousSetData?.weight ?? plannedWeight,
    rpe: existingData?.rpe ?? previousSetData?.rpe ?? undefined,
    notes: existingData?.notes ?? '',
    completed: existingData?.completed ?? false,
  });

  const notesRef = React.useRef<HTMLTextAreaElement>(null);
  const isCompleted = displayData.completed;

  // Auto-populate from previous set when creating new set
  React.useEffect(() => {
    if (!existingData && previousSetData) {
      setDisplayData({
        reps: previousSetData.reps,
        weight: previousSetData.weight,
        rpe: previousSetData.rpe,
        notes: '', // Don't copy notes from previous set
        completed: false,
      });
    }
  }, [existingData, previousSetData]);

  // Update component state when existingData changes from parent
  React.useEffect(() => {
    if (existingData) {
      setDisplayData(prev => {
        // Only update non-completion fields to preserve optimistic updates
        return {
          reps: existingData.reps,
          weight: existingData.weight,
          rpe: existingData.rpe,
          notes: existingData.notes || '',
          completed: prev.completed, // Keep local completion state
        };
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
    setError(null);

    // Only save if this set has been interacted with
    if (existingData || Object.keys(updatedData).length > 0) {
      try {
        setIsSaving(true);
        
        await import('../services/api').then(({ trackExerciseSet }) =>
          trackExerciseSet(exerciseId, setNumber, {
            reps: newData.reps,
            weight: newData.weight,
            rpe: newData.rpe || undefined,
            completed: newData.completed || false,
            notes: newData.notes || undefined,
          })
        );
        
        // Only refresh parent occasionally, not on every completion toggle
        if (updatedData.completed === undefined) {
          onSetUpdated();
        }
        
      } catch (err) {
        console.error('Error persisting set changes:', err);
        setError('Failed to save changes');
        
        // Retry after brief delay
        setTimeout(() => {
          commitSetData(updatedData);
        }, 1000);
        
      } finally {
        setIsSaving(false);
      }
    }
  };

  // Intent-based saving function
  const handleInputBlur = (field: string, value: any) => {
    commitSetData({ [field]: value });
  };

  // Change handlers - update local state immediately, no auto-save
  const handleWeightChange = (value: string) => {
    const weight = parseNumber(value, displayData.weight, 0);
    setDisplayData(prev => ({ ...prev, weight }));
  };

  const handleRepsChange = (value: string) => {
    const reps = parseNumber(value, displayData.reps, 1);
    setDisplayData(prev => ({ ...prev, reps }));
  };

  const handleRpeChange = (value: string) => {
    const rpe = value.trim() ? 
      parseNumber(value, displayData.rpe || 0, 0, 10) : undefined;
    setDisplayData(prev => ({ ...prev, rpe }));
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

  // Truly instant completion toggle - no API dependency
  const handleToggleCompletion = () => {
    if (readOnly) return;

    const newCompletedState = !displayData.completed;
    
    // Instant visual updates (no async, no await)
    setDisplayData(prev => ({ ...prev, completed: newCompletedState }));
    onSetCompletion?.(setNumber, newCompletedState);
    
    // Background save - completely detached from UI
    const saveInBackground = async () => {
      try {
        validateData();
        await import('../services/api').then(({ trackExerciseSet }) =>
          trackExerciseSet(exerciseId, setNumber, {
            reps: displayData.reps,
            weight: displayData.weight,
            rpe: displayData.rpe || undefined,
            completed: newCompletedState,
            notes: displayData.notes || undefined,
          })
        );
        
        // SUCCESS: No UI updates, just silent save
        console.log('✅ Set completion saved silently');
        
      } catch (err: any) {
        console.error('❌ Background save failed:', err);
        // FAILURE: Only revert if save fails
        setDisplayData(prev => ({ ...prev, completed: !newCompletedState }));
        onSetCompletion?.(setNumber, !newCompletedState);
        setError(err.message || 'Failed to save set completion');
      }
    };
    
    // Fire and forget - no UI blocking
    saveInBackground();
  };

  const toggleNotes = () => {
    setNotesExpanded(!notesExpanded);
  };

  return (
    <>
      {/* Set Number */}
      <td className="px-0.5 md:px-2 py-2 text-center font-medium w-10 md:w-16">
        <div className="flex items-center justify-center">
          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
            isCompleted 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-600'
          }`}>
            {setNumber}
          </span>
        </div>
      </td>

      {/* Weight - Wider for values like 110.23 */}
      <td className="px-0.5 md:px-2 py-2 w-20 md:w-32">
        <input
          type="number"
          inputMode="decimal"
          step="0.5"
          value={displayData.weight}
          onChange={(e) => handleWeightChange(e.target.value)}
          onBlur={() => handleInputBlur('weight', displayData.weight)}
          onFocus={(e) => e.target.select()}
          className="w-16 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block"
          disabled={readOnly}
          placeholder={`${plannedWeight}`}
        />
      </td>

      {/* Reps - With onBlur save */}
      <td className="px-0.5 md:px-2 py-2 w-13 md:w-24">

        <input
          type="number"
          inputMode="numeric"
          pattern="[0-9]*"
          value={displayData.reps}
          onChange={(e) => handleRepsChange(e.target.value)}
          onBlur={() => handleInputBlur('reps', displayData.reps)}
          onFocus={(e) => e.target.select()}
          className="w-10 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block"
          disabled={readOnly}
          placeholder={`${plannedReps}`}
        />
      </td>

      {/* RPE - With onBlur save */}
      <td className="px-0.5 md:px-2 py-2 w-13 md:w-24">
        <input
          type="number"
          inputMode="decimal"
          step="0.5"
          min="1"
          max="10"
          value={displayData.rpe || ''}
          onChange={(e) => handleRpeChange(e.target.value)}
          onBlur={() => handleInputBlur('rpe', displayData.rpe)}
          onFocus={(e) => e.target.select()}
          className="w-10 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block"
          placeholder="RPE"
          disabled={readOnly}
        />
      </td>

      {/* Notes */}
      <td className="px-0.5 md:px-2 py-2 w-11 md:w-28">
        <div className="flex justify-center items-center">
          <button
            onClick={toggleNotes}
            className={`w-6 h-6 rounded-full flex items-center justify-center transition-colors ${
              displayData.notes 
                ? 'bg-blue-100 text-blue-600' 
                : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
            }`}
            title={displayData.notes ? 'View notes' : 'Add notes'}
            disabled={readOnly}
          >
            <span className="text-xs">📝</span>
          </button>
        </div>
        {notesExpanded && (
          <div className="absolute z-10 mt-1 p-2 bg-white border border-gray-300 rounded-lg shadow-lg min-w-48">
            <textarea
              ref={notesRef}
              value={displayData.notes}
              onChange={(e) => setDisplayData(prev => ({ ...prev, notes: e.target.value }))}
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
                  commitSetData({ notes: displayData.notes });
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

      {/* Completion Status - Instant Visual Feedback */}
      <td className="px-0.5 md:px-2 py-2 text-center w-11 md:w-16">
        <button
          onClick={handleToggleCompletion}
          disabled={readOnly}
          className={`w-5 h-5 rounded-full flex items-center justify-center mx-auto transition-all duration-200 ${
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
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
export type { SortableInlineSetRowProps };