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
import { useWeightUnit } from '../contexts/UserContext';

interface ExerciseTrackerProps {
  exercise: Exercise;
  onComplete: () => void;
  readOnly?: boolean;
  forceExpanded?: boolean;
}

const ExerciseTracker: React.FC<ExerciseTrackerProps> = ({
  exercise,
  onComplete,
  readOnly = false,
  forceExpanded = false, // Default to false for backward compatibility
}) => {
  const [exerciseState, setExerciseState] = useState<Exercise>(exercise);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  //  Conditional expansion state - only used when NOT force expanded
  const [isExpanded, setIsExpanded] = useState(() => {
    if (forceExpanded) return true; // Always expanded when forced
    
    // Remember expansion state per exercise (existing logic)
    const savedState = localStorage.getItem(`exercise-expanded-${exercise.exercise_id}`);
    return savedState ? JSON.parse(savedState) : false;
  });

  const { getDisplayUnit } = useWeightUnit();
  const displayUnit = getDisplayUnit(exercise.exercise_type);

  // Weight conversion utility functions (matching backend logic)
  const convertKgToLbs = (kg: number): number => {
    const lbs = kg * 2.20462;
    return Math.round(lbs * 2) / 2; // Round to nearest 0.5 lb
  };


  const getDisplayWeight = (storageWeight: number, exerciseType: string): number => {
    const targetUnit = getDisplayUnit(exerciseType);
    
    // Storage is always in kg, convert to display unit if needed
    if (targetUnit === 'lb' && storageWeight > 0) {
      return convertKgToLbs(storageWeight);
    }
    
    return storageWeight; // Already in kg, no conversion needed
  };

  // Convert sets data for display
  const convertSetDataForDisplay = (setData: ExerciseSetData): ExerciseSetData => {
    return {
      ...setData,
      weight: setData.weight > 0 ? getDisplayWeight(setData.weight, exerciseState.exercise_type) : setData.weight
    };
  };

  // Update exercise state when prop changes
  useEffect(() => {
    setExerciseState(exercise);
  }, [exercise]);

  //  Only save expansion state if NOT force expanded
  useEffect(() => {
    if (!forceExpanded) {
      localStorage.setItem(`exercise-expanded-${exerciseState.exercise_id}`, JSON.stringify(isExpanded));
    }
  }, [isExpanded, exerciseState.exercise_id, forceExpanded]);

  // Add drag-and-drop sensors (keeping existing functionality)
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Generate array of set numbers
  const sets = Array.from({ length: exerciseState.sets }, (_, i) => i + 1);

  // Map existing set data by set number for quick lookup
  const setsDataMap = (exerciseState.sets_data || []).reduce((map, setData) => {
    if (setData && typeof setData.set_number === 'number') {
      map[setData.set_number] = setData;
    }
    return map;
  }, {} as Record<number, ExerciseSetData>);

  // Calculate completion status
  const completedSets = exerciseState.sets_data?.filter(set => set.completed).length || 0;
  const allSetsCompleted = completedSets >= exerciseState.sets && exerciseState.sets > 0;
  const progressPercentage = exerciseState.sets > 0 ? (completedSets / exerciseState.sets) * 100 : 0;

  // Get previous set data for auto-population
  const getPreviousSetData = (currentSetNumber: number): ExerciseSetData | undefined => {
    if (currentSetNumber === 1) {
      return undefined; // First set has no previous
    }
    const previousSetData = setsDataMap[currentSetNumber - 1];
    return previousSetData ? convertSetDataForDisplay(previousSetData) : undefined;
  };

  // Handle drag end for set reordering
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
          onComplete(); // Refresh exercise data
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
      
      // Update local state immediately for better UX
      setExerciseState((prev) => ({ ...prev, sets: newSetCount }));

      // Get previous set data to copy values (same logic as getPreviousSetData)
      const previousSetData = newSetCount > 1 ? setsDataMap[newSetCount - 1] : undefined;
      
      let setValuesToUse;
      if (previousSetData) {
        // Convert previous set to display format first (handles kg/lb conversion)
        const displayPreviousSet = convertSetDataForDisplay(previousSetData);
        setValuesToUse = {
          reps: displayPreviousSet.reps,
          weight: displayPreviousSet.weight, // This is now in correct display unit
          rpe: displayPreviousSet.rpe,
        };
      } else {
        // Fallback to planned values if no previous set exists
        setValuesToUse = {
          reps: exerciseState.reps,
          weight: exerciseState.weight, // exerciseState.weight is already in display units
          rpe: exerciseState.rpe,
        };
      }

      // Create placeholder set with previous set values (not planned values)
      await trackExerciseSet(exerciseState.exercise_id, newSetCount, {
        ...setValuesToUse,
        completed: false,
      });

      onComplete(); // Refresh from server
    } catch (err) {
      console.error('Error adding set:', err);
      setExerciseState((prev) => ({ ...prev, sets: prev.sets })); // Revert on error
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
      onComplete(); // Refresh exercise data
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

  // Determine if content should be shown (force expanded OR user expanded)
  const shouldShowContent = forceExpanded || isExpanded;

  // console.log('🔍 STATE SYNC DEBUG:');
  // console.log('🔍 exercise.sets_data:', exercise.sets_data?.map(s => ({ set: s.set_number, weight: s.weight })));
  // console.log('🔍 exerciseState.sets_data:', exerciseState.sets_data?.map(s => ({ set: s.set_number, weight: s.weight })));

  return (
    <div className="space-y-4">
      {/* Conditionally render header - only show when NOT force expanded */}
      {!forceExpanded && (
        <div 
          className="flex justify-between items-start cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">{exerciseState.exercise_type}</h3>
              {/* Exercise completion visual indicator */}
              {exerciseState.status === 'completed' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✓ Complete
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {exerciseState.sets} sets × {exerciseState.reps} reps @ {getDisplayWeight(exerciseState.weight, exerciseState.exercise_type)}{displayUnit}
              {exerciseState.rpe && ` @ RPE ${exerciseState.rpe}`}
            </p>
          </div>
          
          {/* Progress indicator with chevron */}
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
            
            {/* Chevron indicator */}
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

      {/* Conditionally render expanded content - show if force expanded OR user expanded */}
      {shouldShowContent && (
        <>
          {/* Error display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Sets Table - Always visible when expanded */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-8">
                    {/* Drag handle column */}
                  </th>
                  <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                    Set
                  </th>
                  <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                    {displayUnit}
                  </th>
                  <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                    Reps
                  </th>
                  <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                    RPE
                  </th>
                  <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                    Notes
                  </th>
                  <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
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
                      />
                    ))}
                  </SortableContext>
                </DndContext>
              </tbody>
            </table>
          </div>

          {/* Action Buttons - Always visible when expanded */}
          <div className="flex justify-between items-center">
            <div className="flex space-x-2">
              {/* Add Set Button */}
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

              {/* Remove Last Set Button */}
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
              {/* Complete Exercise Button */}
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