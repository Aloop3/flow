import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { setSchema, type SetFormData } from '@/schemas/setSchema';
import { trackExerciseSet } from '../services/api';
import type { ExerciseSetData } from '../services/api';
import { Input } from '@/components/ui/input';

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

      {/* Form Content */}
      <InlineSetRowContent {...props} />
    </tr>
  );
};

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

  // Initial default values - useEffect syncs when existingData changes
  const defaultValues: SetFormData = {
    weight: existingData?.weight ?? previousSetData?.weight ?? plannedWeight,
    reps: existingData?.reps ?? previousSetData?.reps ?? plannedReps,
    rpe: existingData?.rpe ?? previousSetData?.rpe ?? undefined,
    notes: existingData?.notes ?? '',
    completed: existingData?.completed ?? false,
  };

  const form = useForm<SetFormData>({
    resolver: zodResolver(setSchema),
    defaultValues,
  });

  const { watch, setValue, getValues, reset } = form;
  const isCompleted = watch('completed');
  const notes = watch('notes');

  // Track previous existingData to detect first-time data arrival
  const prevExistingDataRef = React.useRef<ExerciseSetData | undefined>(existingData);

  // Only sync form when existingData first becomes available (undefined → defined)
  // This handles async data loading without resetting on every parent re-render
  React.useEffect(() => {
    const prevData = prevExistingDataRef.current;

    if (!prevData && existingData) {
      reset({
        weight: existingData.weight ?? previousSetData?.weight ?? plannedWeight,
        reps: existingData.reps ?? previousSetData?.reps ?? plannedReps,
        rpe: existingData.rpe ?? previousSetData?.rpe ?? undefined,
        notes: existingData.notes ?? '',
        completed: existingData.completed ?? false,
      });
    }

    prevExistingDataRef.current = existingData;
  }, [existingData, previousSetData, plannedWeight, plannedReps, reset]);

  // Save to API
  const saveToApi = async (data: Partial<SetFormData>, skipParentRefresh = false) => {
    const currentValues = getValues();
    const saveData = { ...currentValues, ...data };

    setError(null);
    setIsSaving(true);

    try {
      await trackExerciseSet(exerciseId, setNumber, {
        reps: saveData.reps,
        weight: saveData.weight,
        rpe: saveData.rpe || undefined,
        completed: saveData.completed || false,
        notes: saveData.notes || undefined,
      });

      if (!skipParentRefresh) {
        onSetUpdated();
      }
    } catch (err: any) {
      console.error('Error saving set:', err);
      setError(err.message || 'Failed to save changes');
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  // Handle blur - save individual field
  const handleFieldBlur = async (field: keyof SetFormData) => {
    const value = getValues(field);
    try {
      await saveToApi({ [field]: value });
    } catch {
      // Error already set in saveToApi
    }
  };

  // Handle completion toggle - instant UI, background save
  const handleToggleCompletion = async () => {
    if (readOnly) return;

    const newCompletedState = !isCompleted;

    // Instant UI update
    setValue('completed', newCompletedState);
    onSetCompletion?.(setNumber, newCompletedState);

    // Background save - skip refetch since ExerciseTracker updates state locally
    try {
      await saveToApi({ completed: newCompletedState }, true);
    } catch {
      // Revert on failure
      setValue('completed', !newCompletedState);
      onSetCompletion?.(setNumber, !newCompletedState);
    }
  };

  const toggleNotes = () => {
    setNotesExpanded(!notesExpanded);
  };

  const handleSaveNotes = async () => {
    try {
      await saveToApi({ notes: getValues('notes') });
      setNotesExpanded(false);
    } catch {
      // Error displayed via state
    }
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

      {/* Weight */}
      <td className="px-0.5 md:px-2 py-2 w-20 md:w-32">
        <Input
          type="number"
          inputMode="decimal"
          step={0.5}
          {...form.register('weight', { valueAsNumber: true })}
          onBlur={() => handleFieldBlur('weight')}
          onFocus={(e) => e.target.select()}
          className="w-16 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block h-auto"
          disabled={readOnly}
          placeholder={`${plannedWeight}`}
        />
      </td>

      {/* Reps */}
      <td className="px-0.5 md:px-2 py-2 w-13 md:w-24">
        <Input
          type="number"
          inputMode="numeric"
          {...form.register('reps', { valueAsNumber: true })}
          onBlur={() => handleFieldBlur('reps')}
          onFocus={(e) => e.target.select()}
          className="w-10 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block h-auto"
          disabled={readOnly}
          placeholder={`${plannedReps}`}
        />
      </td>

      {/* RPE */}
      <td className="px-0.5 md:px-2 py-2 w-13 md:w-24">
        <Input
          type="number"
          inputMode="decimal"
          step={0.5}
          min={1}
          max={10}
          {...form.register('rpe', { valueAsNumber: true })}
          onBlur={() => handleFieldBlur('rpe')}
          onFocus={(e) => e.target.select()}
          className="w-10 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block h-auto"
          placeholder="RPE"
          disabled={readOnly}
        />
      </td>

      {/* Notes */}
      <td className="px-0.5 md:px-2 py-2 w-11 md:w-28">
        <div className="flex justify-center items-center">
          <button
            type="button"
            onClick={toggleNotes}
            className={`w-6 h-6 rounded-full flex items-center justify-center transition-colors ${
              notes
                ? 'bg-blue-100 text-blue-600'
                : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
            }`}
            title={notes ? 'View notes' : 'Add notes'}
            disabled={readOnly}
          >
            <span className="text-xs">📝</span>
          </button>
        </div>
        {notesExpanded && (
          <div className="absolute z-10 mt-1 p-2 bg-white border border-gray-300 rounded-lg shadow-lg min-w-48">
            <textarea
              {...form.register('notes')}
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
                type="button"
                onClick={handleSaveNotes}
                className="px-2 py-1 text-xs text-blue-600 hover:text-blue-800"
                disabled={isSaving}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
              <button
                type="button"
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
      <td className="px-0.5 md:px-2 py-2 text-center w-11 md:w-16">
        <button
          type="button"
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
