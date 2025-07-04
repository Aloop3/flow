import React, { useState, useEffect } from 'react';
import { 
  DndContext, 
  closestCenter, 
  KeyboardSensor, 
  PointerSensor, 
  useSensor, 
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { trackExerciseSet, deleteSet, completeExercise, reorderExerciseSets } from '../services/api';
import type { Exercise, ExerciseSetData } from '../services/api';
import FormButton from './FormButton';
import SortableInlineSetRow from './SortableInlineSetRow';

interface ExerciseTrackerProps {
  exercise: Exercise;
  onComplete: () => void;
  readOnly?: boolean;
  forceExpanded?: boolean;
  onProgressUpdate?: (completed: number, total: number) => void;
}

const roundDisplayWeight = (weight: number): number => {
  return weight > 0 ? Math.round(weight * 10) / 10 : weight;
};

const ExerciseTracker: React.FC<ExerciseTrackerProps> = ({
  exercise,
  onComplete,
  readOnly = false,
  forceExpanded = false,
  onProgressUpdate,
}) => {
  const [exerciseState, setExerciseState] = useState<Exercise>(exercise);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Local sets completion tracking for instant progress updates
  const [localSetsCompletion, setLocalSetsCompletion] = useState<Record<number, boolean>>({});
  
  const [isExpanded, setIsExpanded] = useState(() => {
    if (forceExpanded) return true;
    
    const savedState = localStorage.getItem(`exercise-expanded-${exercise.exercise_id}`);
    return savedState ? JSON.parse(savedState) : false;
  });

  const displayUnit = exercise.display_unit || 'lb';
  

  const convertSetDataForDisplay = (setData: ExerciseSetData): ExerciseSetData => {
    return {
      ...setData,
      weight: roundDisplayWeight(setData.weight)
    };
  };


  useEffect(() => {
    setExerciseState(exercise);
  }, [exercise]);

  // Initialize local completion state from exercise data
  useEffect(() => {
    const completionMap = (exerciseState.sets_data || []).reduce((map, setData) => {
      if (setData && typeof setData.set_number === 'number') {
        map[setData.set_number] = setData.completed || false;
      }
      return map;
    }, {} as Record<number, boolean>);
    setLocalSetsCompletion(completionMap);
  }, [exerciseState.sets_data]);

  useEffect(() => {
    if (!forceExpanded) {
      localStorage.setItem(`exercise-expanded-${exerciseState.exercise_id}`, JSON.stringify(isExpanded));
    }
  }, [isExpanded, exerciseState.exercise_id, forceExpanded]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const sets = Array.from({ length: exerciseState.sets }, (_, i) => i + 1);

  const setsDataMap = (exerciseState.sets_data || []).reduce((map, setData) => {
    if (setData && typeof setData.set_number === 'number') {
      map[setData.set_number] = setData;
    }
    return map;
  }, {} as Record<number, ExerciseSetData>);

  // Calculate progress from local state for instant updates
  const completedSets = Object.values(localSetsCompletion).filter(Boolean).length;
  const allSetsCompleted = completedSets >= exerciseState.sets && exerciseState.sets > 0;
  const progressPercentage = exerciseState.sets > 0 ? (completedSets / exerciseState.sets) * 100 : 0;

  // Optimistic set completion handler for instant progress updates
  const handleSetCompletion = (setNumber: number, completed: boolean) => {
    setLocalSetsCompletion(prev => {
      const updated = { ...prev, [setNumber]: completed };
      const newCompleted = Object.values(updated).filter(Boolean).length;
      onProgressUpdate?.(newCompleted, exerciseState.sets);
      return updated;
    });
  };

  const getPreviousSetData = (currentSetNumber: number): ExerciseSetData | undefined => {
    if (currentSetNumber === 1) {
      return undefined;
    }
    const previousSetData = setsDataMap[currentSetNumber - 1];
    return previousSetData ? convertSetDataForDisplay(previousSetData) : undefined;
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (active.id !== over?.id) {
      const oldIndex = sets.findIndex(setNum => setNum === active.id);
      const newIndex = sets.findIndex(setNum => setNum === over?.id);

      if (oldIndex !== -1 && newIndex !== -1) {
        const newOrder = arrayMove(sets, oldIndex, newIndex);
        
        try {
          setIsSubmitting(true);
          setError(null);
          
          await reorderExerciseSets(exerciseState.exercise_id, newOrder);
          onComplete();
        } catch (err: any) {
          console.error('Error reordering sets:', err);
          setError('Failed to reorder sets. Please try again.');
        } finally {
          setIsSubmitting(false);
        }
      }
    }
  };

  const addSet = async () => {
    if (readOnly) return;
    setIsSubmitting(true);
    setError(null);

    try {
      const newSetCount = exerciseState.sets + 1;
      
      setExerciseState((prev) => ({ ...prev, sets: newSetCount }));

      const previousSetData = newSetCount > 1 ? setsDataMap[newSetCount - 1] : undefined;
      
      let setValuesToUse;
      if (previousSetData) {
        const displayPreviousSet = convertSetDataForDisplay(previousSetData);
        setValuesToUse = {
          reps: displayPreviousSet.reps,
          weight: displayPreviousSet.weight,
          rpe: displayPreviousSet.rpe,
        };
      } else {
        setValuesToUse = {
          reps: exerciseState.reps,
          weight: exerciseState.weight,
          rpe: exerciseState.rpe,
        };
      }

      await trackExerciseSet(exerciseState.exercise_id, newSetCount, {
        ...setValuesToUse,
        completed: false,
      });

      onComplete();
    } catch (err) {
      console.error('Error adding set:', err);
      setExerciseState((prev) => ({ ...prev, sets: prev.sets }));
      setError('Failed to add set. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const removeSet = async (setNumber: number) => {
    if (readOnly || exerciseState.sets <= 1) return;
    
    setIsSubmitting(true);
    setError(null);

    try {
      await deleteSet(exerciseState.exercise_id, setNumber);
      onComplete();
    } catch (err: any) {
      console.error('Error removing set:', err);
      setError('Failed to remove set. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCompleteExercise = async () => {
    if (readOnly) return;
    
    setIsSubmitting(true);
    setError(null);

    try {
      await completeExercise(exerciseState.exercise_id, {
        sets: exerciseState.sets,
        reps: exerciseState.reps,
        weight: exerciseState.weight,
        rpe: exerciseState.rpe,
        notes: exerciseState.notes,
      });
      onComplete();
    } catch (err: any) {
      console.error('Error completing exercise:', err);
      setError('Failed to complete exercise. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const shouldShowContent = forceExpanded || isExpanded;

  return (
    <div className="space-y-4">
      {!forceExpanded && (
        <div 
          className="flex justify-between items-start cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">{exerciseState.exercise_type}</h3>
              {exerciseState.status === 'completed' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✓ Complete
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {exerciseState.sets} sets × {exerciseState.reps} reps @ {roundDisplayWeight(exerciseState.weight)}{displayUnit}
              {exerciseState.rpe && ` @ RPE ${exerciseState.rpe}`}
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-700">
                {completedSets}/{exerciseState.sets} sets
              </div>
              <div className="w-20 h-2 bg-gray-200 rounded-full mt-1">
                <div
                  className="h-2 bg-blue-500 rounded-full transition-all"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
            </div>
            
            <div className="flex items-center">
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
        </div>
      )}

      {shouldShowContent && (
        <>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Sets Table - No Scroll Layout */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-0.5 md:px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-4 md:w-8">
                    {/* Drag handle column */}
                  </th>
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
                <DndContext
                  sensors={sensors}
                  collisionDetection={closestCenter}
                  onDragEnd={handleDragEnd}
                >
                  <SortableContext items={sets} strategy={verticalListSortingStrategy}>
                    {sets.map((setNumber) => (
                      <SortableInlineSetRow
                        key={setNumber}
                        exerciseId={exerciseState.exercise_id}
                        setNumber={setNumber}
                        existingData={setsDataMap[setNumber] ? convertSetDataForDisplay(setsDataMap[setNumber]) : undefined}
                        previousSetData={getPreviousSetData(setNumber)}
                        plannedReps={exerciseState.reps}
                        plannedWeight={exerciseState.weight}
                        readOnly={readOnly}
                        onSetUpdated={onComplete}
                        onSetCompletion={handleSetCompletion}
                      />
                    ))}
                  </SortableContext>
                </DndContext>
              </tbody>
            </table>
          </div>

          <div className="flex justify-between items-center">
            <div className="flex space-x-2">
              {!readOnly && (
                <FormButton
                  type="button"
                  variant="secondary"
                  onClick={addSet}
                  disabled={isSubmitting}
                  isLoading={isSubmitting}
                >
                  Add Set
                </FormButton>
              )}

              {!readOnly && 
                exerciseState.sets > 1 && 
                !(allSetsCompleted && exerciseState.status !== 'completed') && (
                <FormButton
                  type="button"
                  variant="secondary"
                  onClick={() => removeSet(exerciseState.sets)}
                  disabled={isSubmitting}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  Remove Last Set
                </FormButton>
              )}
            </div>

            <div className="flex space-x-2">
              {!readOnly && 
                exerciseState.status !== 'completed' && 
                allSetsCompleted && (
                <FormButton
                  type="button"
                  variant="primary"
                  onClick={handleCompleteExercise}
                  disabled={isSubmitting}
                  isLoading={isSubmitting}
                >
                  Complete Exercise
                </FormButton>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ExerciseTracker;