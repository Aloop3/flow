import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { completeExercise } from '../services/api';
import type { Exercise } from '../services/api';
import type { SetData } from '../services/workoutStorage';

interface ExerciseCardProps {
  exercise: Exercise;
  setsData: Record<number, SetData>;
  onUpdateSet: (setNumber: number, data: Partial<SetData>) => void;
  onToggleCompletion: (setNumber: number) => void;
  onExerciseComplete?: () => void;
  onUncompleteExercise?: () => Promise<void>;
  onAddSet?: () => Promise<void>;
  onDeleteSet?: (setNumber: number) => Promise<void>;
  readOnly?: boolean;
  forceExpanded?: boolean;
}

const roundDisplayWeight = (weight: number): number => {
  return weight > 0 ? Math.round(weight * 10) / 10 : weight;
};

const ExerciseCard: React.FC<ExerciseCardProps> = ({
  exercise,
  setsData,
  onUpdateSet,
  onToggleCompletion,
  onExerciseComplete,
  onUncompleteExercise,
  onAddSet,
  onDeleteSet,
  readOnly = false,
  forceExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(() => {
    if (forceExpanded) return true;
    const saved = localStorage.getItem(`exercise-expanded-${exercise.exercise_id}`);
    return saved ? JSON.parse(saved) : false;
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Local status for optimistic toggle updates only
  const [localStatus, setLocalStatus] = useState(exercise.status);

  // Sync local status when props change
  useEffect(() => {
    setLocalStatus(exercise.status);
  }, [exercise.status]);

  const displayUnit = exercise.display_unit || 'lb';
  const totalSets = exercise.sets; // Use server count (stable)

  // Calculate completion from setsData, capped at totalSets
  let completedSets = 0;
  for (let i = 1; i <= totalSets; i++) {
    if (setsData[i]?.completed) completedSets++;
  }
  const allSetsCompleted = completedSets >= totalSets && totalSets > 0;
  const progressPercentage = totalSets > 0 ? (completedSets / totalSets) * 100 : 0;

  // Save expanded state to localStorage
  useEffect(() => {
    if (!forceExpanded) {
      localStorage.setItem(`exercise-expanded-${exercise.exercise_id}`, JSON.stringify(isExpanded));
    }
  }, [isExpanded, exercise.exercise_id, forceExpanded]);

  const toggleExpanded = () => {
    if (!forceExpanded) {
      setIsExpanded(!isExpanded);
    }
  };

  const handleCompleteExercise = async () => {
    if (readOnly) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await completeExercise(exercise.exercise_id, {
        sets: exercise.sets,
        reps: exercise.reps,
        weight: exercise.weight,
        rpe: exercise.rpe,
        notes: exercise.notes,
      });
      onExerciseComplete?.();
    } catch (err: unknown) {
      console.error('Error completing exercise:', err);
      setError('Failed to complete exercise. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddSet = async () => {
    if (readOnly || !onAddSet) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await onAddSet();
    } catch (err: unknown) {
      console.error('Error adding set:', err);
      setError('Failed to add set. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const shouldShowContent = forceExpanded || isExpanded;

  // Handler for toggling set completion - also updates exercise status if needed
  const handleToggleSetCompletion = (setNumber: number) => {
    const currentSetData = getSetDataWithFallback(setNumber);
    const isCurrentlyCompleted = currentSetData.completed;

    // Toggle the set completion immediately (optimistic update)
    onToggleCompletion(setNumber);

    // If exercise is completed and we're un-toggling a set, update status immediately
    if (localStatus === 'completed' && isCurrentlyCompleted) {
      setLocalStatus('planned'); // Optimistic update
      if (onUncompleteExercise) {
        // Fire and forget - don't block UI
        onUncompleteExercise().catch(err => {
          console.error('Failed to update exercise status:', err);
        });
      }
    }
  };

  // Helper to get set data with proper fallback to server data
  const getSetDataWithFallback = (setNumber: number): SetData => {
    // First try localStorage data
    if (setsData[setNumber]) {
      return setsData[setNumber];
    }
    // Fallback to server data (preserves completed status)
    const serverSetData = exercise.sets_data?.find(s => s.set_number === setNumber);
    return {
      weight: serverSetData?.weight ?? exercise.weight,
      reps: serverSetData?.reps ?? exercise.reps,
      rpe: serverSetData?.rpe ?? exercise.rpe,
      completed: serverSetData?.completed ?? false,
    };
  };

  return (
    <div className="border rounded-lg bg-white shadow-sm overflow-hidden">
      {/* Header - Always visible */}
      {!forceExpanded && (
        <div
          className="flex justify-between items-start cursor-pointer hover:bg-gray-50 p-4 transition-colors"
          onClick={toggleExpanded}
        >
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">{exercise.exercise_type}</h3>
              {exercise.status === 'completed' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✓ Complete
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {totalSets} sets × {exercise.reps} reps @ {roundDisplayWeight(exercise.weight)}{displayUnit}
              {exercise.rpe && ` @ RPE ${exercise.rpe}`}
            </p>
          </div>

          <div className="flex items-center space-x-3">
            {/* Progress indicator */}
            <div className="text-right">
              <div className="text-sm font-medium text-gray-700">
                {completedSets}/{totalSets} sets
              </div>
              <div className="w-20 h-2 bg-gray-200 rounded-full mt-1">
                <div
                  className="h-2 bg-blue-500 rounded-full transition-all"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
            </div>

            {/* Expand icon */}
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      )}

      {/* Expanded content - Sets table */}
      {shouldShowContent && (
        <div className={forceExpanded ? 'p-4' : 'border-t px-4 pb-4'}>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-0.5 md:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-10 md:w-16">
                    Set
                  </th>
                  <th className="px-0.5 md:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20 md:w-32">
                    {displayUnit}
                  </th>
                  <th className="px-0.5 md:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-13 md:w-24">
                    Reps
                  </th>
                  <th className="px-0.5 md:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-13 md:w-24">
                    RPE
                  </th>
                  <th className="px-0.5 md:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-11 md:w-28">
                    Notes
                  </th>
                  <th className="px-0.5 md:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-11 md:w-16">
                    ✓
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Array.from({ length: totalSets }, (_, i) => i + 1).map(setNumber => (
                  <SetRow
                    key={setNumber}
                    setNumber={setNumber}
                    setData={getSetDataWithFallback(setNumber)}
                    onUpdate={(data) => onUpdateSet(setNumber, data)}
                    onToggleCompletion={() => handleToggleSetCompletion(setNumber)}
                    onDelete={onDeleteSet ? () => onDeleteSet(setNumber) : undefined}
                    readOnly={readOnly}
                    canDelete={!readOnly && totalSets > 1 && !!onDeleteSet}
                  />
                ))}
              </tbody>
            </table>
          </div>

          {/* Action buttons - stacked on mobile, row on desktop */}
          <div className="flex flex-col sm:flex-row sm:justify-between gap-3 mt-4">
            <div className="flex flex-wrap gap-2">
              {!readOnly && onAddSet && (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleAddSet}
                  disabled={isSubmitting}
                  className="flex-1 sm:flex-none"
                >
                  {isSubmitting ? 'Adding...' : 'Add Set'}
                </Button>
              )}
            </div>

            <div className="flex justify-center sm:justify-end">
              {localStatus === 'completed' && (
                <span className="inline-flex items-center px-3 py-2 text-sm font-medium text-green-700 bg-green-50 rounded-md">
                  ✓ Completed
                </span>
              )}
              {!readOnly && allSetsCompleted && localStatus !== 'completed' && (
                <Button
                  onClick={handleCompleteExercise}
                  disabled={isSubmitting}
                  className="w-full sm:w-auto"
                >
                  {isSubmitting ? 'Completing...' : 'Complete Exercise'}
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Individual set row with click-to-delete support
 */
interface SetRowProps {
  setNumber: number;
  setData: SetData;
  onUpdate: (data: Partial<SetData>) => void;
  onToggleCompletion: () => void;
  onDelete?: () => void;
  readOnly: boolean;
  canDelete: boolean;
}

const SetRow: React.FC<SetRowProps> = ({
  setNumber,
  setData,
  onUpdate,
  onToggleCompletion,
  onDelete,
  readOnly,
  canDelete,
}) => {
  // Local form state - initialized from setData, syncs to localStorage on blur
  const [weight, setWeight] = useState<string>(String(setData.weight || ''));
  const [reps, setReps] = useState<string>(String(setData.reps || ''));
  const [rpe, setRpe] = useState<string>(setData.rpe ? String(setData.rpe) : '');
  const [notes, setNotes] = useState<string>(setData.notes || '');

  // Delete mode state - toggled by clicking set number
  const [deleteMode, setDeleteMode] = useState(false);
  const [notesExpanded, setNotesExpanded] = useState(false);

  // Auto-cancel delete mode after 5 seconds
  useEffect(() => {
    if (deleteMode) {
      const timer = setTimeout(() => setDeleteMode(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [deleteMode]);

  // Sync local state when setData changes (e.g., from localStorage reload)
  useEffect(() => {
    setWeight(String(setData.weight || ''));
    setReps(String(setData.reps || ''));
    setRpe(setData.rpe ? String(setData.rpe) : '');
    setNotes(setData.notes || '');
  }, [setData.weight, setData.reps, setData.rpe, setData.notes]);

  const handleBlur = (field: 'weight' | 'reps' | 'rpe', value: string) => {
    const numValue = parseFloat(value) || 0;
    // Only update if value actually changed
    if (field === 'weight' && numValue !== setData.weight) {
      onUpdate({ weight: numValue });
    } else if (field === 'reps' && numValue !== setData.reps) {
      onUpdate({ reps: numValue });
    } else if (field === 'rpe' && numValue !== (setData.rpe || 0)) {
      onUpdate({ rpe: numValue || undefined });
    }
  };

  const handleSaveNotes = () => {
    if (notes !== (setData.notes || '')) {
      onUpdate({ notes: notes || undefined });
    }
    setNotesExpanded(false);
  };

  // Click handler for set number - toggles delete mode or confirms delete
  const handleSetNumberClick = () => {
    if (!canDelete || readOnly) return;

    if (deleteMode) {
      // Second click - confirm delete
      if (onDelete) {
        onDelete();
      }
      setDeleteMode(false);
    } else {
      // First click - enter delete mode
      setDeleteMode(true);
    }
  };

  return (
    <tr className={`border-b hover:bg-gray-50 ${deleteMode ? 'bg-red-50' : ''}`}>
      {/* Set number - click to toggle delete mode, click again to delete */}
      <td className="px-0.5 md:px-2 py-2 text-center font-medium w-10 md:w-16">
        <div className="flex items-center justify-center">
          <button
            type="button"
            onClick={handleSetNumberClick}
            disabled={!canDelete || readOnly}
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium transition-colors ${
              deleteMode
                ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
                : setData.completed
                  ? 'bg-green-100 text-green-800'
                  : canDelete && !readOnly
                    ? 'bg-gray-100 text-gray-600 hover:bg-gray-200 cursor-pointer'
                    : 'bg-gray-100 text-gray-600'
            }`}
            title={deleteMode ? 'Click to delete' : canDelete ? 'Click to remove set' : undefined}
          >
            {deleteMode ? '−' : setNumber}
          </button>
        </div>
      </td>

      {/* Weight */}
      <td className="px-0.5 md:px-2 py-2 w-20 md:w-32">
        <Input
          type="number"
          inputMode="decimal"
          step={0.5}
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          onBlur={(e) => handleBlur('weight', e.target.value)}
          onFocus={(e) => e.target.select()}
          className="w-16 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block h-auto"
          disabled={readOnly}
        />
      </td>

      {/* Reps */}
      <td className="px-0.5 md:px-2 py-2 w-13 md:w-24">
        <Input
          type="number"
          inputMode="numeric"
          value={reps}
          onChange={(e) => setReps(e.target.value)}
          onBlur={(e) => handleBlur('reps', e.target.value)}
          onFocus={(e) => e.target.select()}
          className="w-10 px-1 py-1 text-xs text-center bg-transparent border-0 hover:border hover:border-gray-300 focus:border-blue-500 focus:bg-white rounded transition-all mx-auto block h-auto"
          disabled={readOnly}
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
          value={rpe}
          onChange={(e) => setRpe(e.target.value)}
          onBlur={(e) => handleBlur('rpe', e.target.value)}
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
            onClick={() => setNotesExpanded(!notesExpanded)}
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
        {/* Notes Modal Overlay */}
        {notesExpanded && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-4">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-medium text-gray-900">Set {setNumber} Notes</h3>
                <button
                  type="button"
                  onClick={() => setNotesExpanded(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Escape') setNotesExpanded(false);
                }}
                className="w-full px-3 py-2 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
                placeholder="Add notes for this set..."
                disabled={readOnly}
                autoFocus
              />
              <div className="flex justify-end mt-4 space-x-3">
                <button
                  type="button"
                  onClick={() => setNotesExpanded(false)}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveNotes}
                  className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg"
                >
                  Save Notes
                </button>
              </div>
            </div>
          </div>
        )}
      </td>

      {/* Completion checkbox */}
      <td className="px-0.5 md:px-2 py-2 text-center w-11 md:w-16">
        <button
          type="button"
          onClick={onToggleCompletion}
          disabled={readOnly}
          className={`w-5 h-5 rounded-full flex items-center justify-center mx-auto transition-all duration-200 ${
            readOnly
              ? 'cursor-not-allowed opacity-50'
              : 'cursor-pointer hover:scale-110 transform'
          } ${
            setData.completed
              ? 'bg-green-500 text-white hover:bg-green-600 shadow-md'
              : 'border-2 border-gray-300 hover:border-green-400 hover:bg-green-50'
          }`}
          title={setData.completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {setData.completed && (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>
      </td>
    </tr>
  );
};

export default ExerciseCard;
