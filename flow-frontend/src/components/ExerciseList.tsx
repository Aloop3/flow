import { useState, useEffect } from 'react';
import type { Exercise } from '../services/api';
import { createExercise, deleteExercise, trackExerciseSet, deleteSet, updateExercise, reorderExercises } from '../services/api';
import ExerciseTracker from './ExerciseTracker';
import ExerciseCard from './ExerciseCard';
import ExerciseSelector from './ExerciseSelector';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { fetchAuthSession } from 'aws-amplify/auth';
import { useWorkoutDraft } from '../hooks/useWorkoutDraft';

// Feature flag - flip to false to rollback to old implementation
const USE_LOCAL_FIRST_WORKOUT = true;

interface ExerciseListProps {
  exercises: Exercise[];
  workoutId?: string;
  dayId?: string; // Required for local-first mode
  onExerciseComplete: () => void;
  readOnly?: boolean;
  athleteId?: string;
}

const ExerciseList = ({ athleteId, exercises, workoutId, dayId, onExerciseComplete, readOnly = false }: ExerciseListProps) => {
  const [expandedExerciseId, setExpandedExerciseId] = useState<string | null>(null);
  const [isAddingExercise, setIsAddingExercise] = useState(false);
  const [selectedExerciseType, setSelectedExerciseType] = useState<string>('');
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string>();

  // Local progress tracking for instant updates (used in legacy mode)
  const [localProgressMap, setLocalProgressMap] = useState<Record<string, { completed: number; total: number }>>({});

  // Optimistic exercise order for instant reorder UI
  const [optimisticExercises, setOptimisticExercises] = useState<Exercise[]>(exercises);

  // Local-first workout draft hook (only active when flag is enabled and dayId is provided)
  const workoutDraft = useWorkoutDraft(
    USE_LOCAL_FIRST_WORKOUT && dayId ? dayId : '',
    USE_LOCAL_FIRST_WORKOUT && dayId ? exercises : []
  );

  useEffect(() => {
    const getUserId = async () => {
      try {
        const { tokens } = await fetchAuthSession();
        const userIdFromToken = tokens?.idToken?.payload?.sub as string;
        setUserId(userIdFromToken);
      } catch (error) {
        console.error('Error getting user ID for custom exercises:', error);
      }
    };

    getUserId();
  }, []);

  // Initialize local progress map from exercises
  useEffect(() => {
    const progressMap = exercises.reduce((map, exercise) => {
      const completedSets = exercise.sets_data?.filter(set => set.completed).length || 0;
      map[exercise.exercise_id] = {
        completed: completedSets,
        total: exercise.sets
      };
      return map;
    }, {} as Record<string, { completed: number; total: number }>);
    setLocalProgressMap(progressMap);
  }, [exercises]);

  // Sync optimistic exercises when prop changes (after backend refresh)
  useEffect(() => {
    setOptimisticExercises(exercises);
  }, [exercises]);

  // Use athleteId when provided (coach context), otherwise current user
  const userIdForExercises = athleteId || userId;

  // Toggle expansion instead of opening modal
  const handleExerciseClick = (exercise: Exercise) => {
    if (!readOnly) {
      setExpandedExerciseId(
        expandedExerciseId === exercise.exercise_id ? null : exercise.exercise_id
      );
    }
  };

  const handleComplete = () => {
    // Preserve scroll position during workout refresh
    const scrollY = window.scrollY;

    // Call the parent refresh function
    onExerciseComplete();

    // Restore scroll position after React re-render completes
    requestAnimationFrame(() => {
      window.scrollTo(0, scrollY);
    });
  };

  // Handler for adding a set to an exercise (optimistic UI)
  const handleAddSet = async (exercise: Exercise) => {
    const scrollY = window.scrollY;
    const newSetCount = exercise.sets + 1;

    // Get previous set data for default values, with fallbacks to exercise defaults
    const setsData = workoutDraft.getExerciseSets(exercise.exercise_id);
    const previousSet = setsData[exercise.sets];

    // Use previous set values if valid, otherwise fall back to exercise defaults
    const setValues = {
      reps: previousSet?.reps || exercise.reps || 1,
      weight: previousSet?.weight ?? exercise.weight ?? 0,
      rpe: previousSet?.rpe || exercise.rpe,
    };

    // Initialize the new set in localStorage immediately
    workoutDraft.updateSet(exercise.exercise_id, newSetCount, {
      ...setValues,
      completed: false,
    });

    // Optimistic UI: Update local exercise list with incremented set count
    setOptimisticExercises(prev =>
      prev.map(ex =>
        ex.exercise_id === exercise.exercise_id
          ? { ...ex, sets: newSetCount }
          : ex
      )
    );

    // Fire backend call silently
    trackExerciseSet(exercise.exercise_id, newSetCount, {
      ...setValues,
      completed: false,
    }).catch(err => {
      // Revert on failure
      setOptimisticExercises(exercises);
      setError('Failed to add set. Please try again.');
      console.error('Error adding set:', err);
    });

    requestAnimationFrame(() => {
      window.scrollTo(0, scrollY);
    });
  };

  // Handler for deleting a specific set (click-to-delete)
  const handleDeleteSet = async (exercise: Exercise, setNumber: number) => {
    if (exercise.sets <= 1) return; // Can't delete if only 1 set

    const scrollY = window.scrollY;
    const newSetCount = exercise.sets - 1;

    // Remove from localStorage first for instant UI update
    workoutDraft.removeSet(exercise.exercise_id, setNumber);

    // Optimistic UI: Update local exercise list with decremented set count
    setOptimisticExercises(prev =>
      prev.map(ex =>
        ex.exercise_id === exercise.exercise_id
          ? { ...ex, sets: newSetCount }
          : ex
      )
    );

    // Fire backend call silently
    deleteSet(exercise.exercise_id, setNumber).catch(err => {
      // Revert on failure
      setOptimisticExercises(exercises);
      setError('Failed to delete set. Please try again.');
      console.error('Error deleting set:', err);
    });

    requestAnimationFrame(() => {
      window.scrollTo(0, scrollY);
    });
  };

  // Handler for marking a completed exercise as incomplete (when user untoggles a set)
  const handleUncompleteExercise = async (exercise: Exercise) => {
    if (exercise.status !== 'completed') return;

    const scrollY = window.scrollY;
    await updateExercise(exercise.exercise_id, { status: 'planned' });

    onExerciseComplete();
    requestAnimationFrame(() => {
      window.scrollTo(0, scrollY);
    });
  };

  const handleAddExercise = async () => {
    if (!selectedExerciseType || !workoutId) return;
    
    try {
      setError(null);
      
      // Preserve scroll position
      const scrollY = window.scrollY;
      
      // Create exercise with default values
      await createExercise({
        workout_id: workoutId,
        exercise_type: selectedExerciseType,
        sets: 1,
        reps: 1,
        weight: 0,
        rpe: 6,
        status: 'planned',
        notes: '',
      });
      
      // Reset and refresh
      setIsAddingExercise(false);
      setSelectedExerciseType('');
      onExerciseComplete(); // This refreshes the workout data
      
      // Restore scroll position
      requestAnimationFrame(() => {
        window.scrollTo(0, scrollY);
      });
    } catch (err) {
      setError('Failed to add exercise. Please try again.');
      console.error('Error adding exercise:', err);
    }
  };

  const handleRemoveExercise = async (exerciseId: string) => {
    try {
      setIsDeleting(exerciseId);
      setError(null);

      // MOBILE SCROLL FIX: Preserve scroll position
      const scrollY = window.scrollY;

      await deleteExercise(exerciseId);

      // Collapse if this exercise was expanded
      if (expandedExerciseId === exerciseId) {
        setExpandedExerciseId(null);
      }

      // Refresh the workout data
      onExerciseComplete();

      // Restore scroll position
      requestAnimationFrame(() => {
        window.scrollTo(0, scrollY);
      });
    } catch (err) {
      setError('Failed to remove exercise. Please try again.');
      console.error('Error removing exercise:', err);
    } finally {
      setIsDeleting(null);
    }
  };

  // Handler for moving exercises up/down (optimistic UI)
  const handleMoveExercise = (exerciseId: string, direction: 'up' | 'down') => {
    if (!workoutId) return;

    const currentIndex = optimisticExercises.findIndex(e => e.exercise_id === exerciseId);
    if (currentIndex === -1) return;

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= optimisticExercises.length) return;

    // Optimistic update - instant UI feedback
    const reordered = [...optimisticExercises];
    [reordered[currentIndex], reordered[newIndex]] = [reordered[newIndex], reordered[currentIndex]];
    setOptimisticExercises(reordered);

    // Build order array and fire API silently
    const newOrder = reordered.map(e => e.exercise_id);
    reorderExercises(workoutId, newOrder).catch(err => {
      // Revert on failure
      setOptimisticExercises(exercises);
      setError('Failed to reorder exercises. Please try again.');
      console.error('Error reordering exercises:', err);
    });
  };

  // Get set progress with local progress fallback for instant updates
  const getSetProgress = (exercise: Exercise) => {
    // Use local-first data when enabled
    if (USE_LOCAL_FIRST_WORKOUT && dayId) {
      return workoutDraft.getExerciseCompletion(exercise.exercise_id, exercise.sets);
    }

    // Legacy: Use local progress if available, otherwise calculate from exercise data
    const localProgress = localProgressMap[exercise.exercise_id];
    if (localProgress) {
      return localProgress;
    }

    // Fallback to exercise data calculation
    if (!exercise.sets_data || exercise.sets_data.length === 0) {
      return { completed: 0, total: exercise.sets };
    }

    const completedSets = exercise.sets_data.filter(set => set.completed).length;
    return {
      completed: completedSets,
      total: exercise.sets
    };
  };

  // Handler for exercise progress updates from ExerciseTracker
  const handleExerciseProgressUpdate = (exerciseId: string, completed: number, total: number) => {
    setLocalProgressMap(prev => ({
      ...prev,
      [exerciseId]: { completed, total }
    }));
  };

  return (
    <>
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}
      
      <div className="divide-y divide-ocean-slate/30">
        {optimisticExercises.map((exercise) => {
          const setProgress = getSetProgress(exercise);
          const hasSetData = exercise.sets_data && exercise.sets_data.length > 0;
          const isExpanded = expandedExerciseId === exercise.exercise_id;
          
          return (
            <div key={exercise.exercise_id} className="py-3">
              {/* Exercise Summary Row */}
              <div className={`px-4 ${
                !readOnly && exercise.status !== 'completed' ? 'cursor-pointer' : ''
              }`}>
                {/* Top row: Exercise name + overflow menu */}
                <div className="flex justify-between items-start">
                  <div
                    className="flex-grow"
                    onClick={() => handleExerciseClick(exercise)}
                  >
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium">{exercise.exercise_type}</h3>
                      {!readOnly && (
                        <svg
                          className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      )}
                    </div>

                    {exercise.notes && (
                      <p className="mt-1 text-xs text-gray-500">{exercise.notes}</p>
                    )}
                  </div>

                  {/* Overflow menu - top right */}
                  {!readOnly && workoutId && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button
                          onClick={(e) => e.stopPropagation()}
                          disabled={isDeleting === exercise.exercise_id}
                          className="text-gray-400 hover:text-gray-600 disabled:text-gray-300 p-1 rounded hover:bg-gray-100"
                          title="More options"
                        >
                          {isDeleting === exercise.exercise_id ? (
                            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                            </svg>
                          ) : (
                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                            </svg>
                          )}
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRemoveExercise(exercise.exercise_id);
                          }}
                          className="text-red-600 focus:text-red-600 focus:bg-red-50"
                        >
                          <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          Remove Exercise
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>

                {/* Progress bar and reorder buttons row */}
                <div className="mt-2 flex items-center space-x-2" onClick={() => handleExerciseClick(exercise)}>
                  {/* Progress bar - shows if has data */}
                  {(hasSetData || setProgress.completed > 0) ? (
                    <div className="flex-grow">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Set progress</span>
                        <span>{setProgress.completed} / {setProgress.total} sets</span>
                      </div>
                      <div className="bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-ocean-teal h-2 rounded-full transition-all duration-300"
                          style={{ width: `${setProgress.total > 0 ? (setProgress.completed / setProgress.total) * 100 : 0}%` }}
                        ></div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-grow" />
                  )}
                  {/* Reorder buttons - always visible when editable */}
                  {!readOnly && workoutId && (
                    <div className="flex items-center space-x-0.5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMoveExercise(exercise.exercise_id, 'up');
                        }}
                        disabled={optimisticExercises.findIndex(e => e.exercise_id === exercise.exercise_id) === 0}
                        className="text-gray-400 hover:text-ocean-teal disabled:text-gray-200 disabled:cursor-not-allowed p-0.5"
                        title="Move up"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                        </svg>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMoveExercise(exercise.exercise_id, 'down');
                        }}
                        disabled={optimisticExercises.findIndex(e => e.exercise_id === exercise.exercise_id) === optimisticExercises.length - 1}
                        className="text-gray-400 hover:text-ocean-teal disabled:text-gray-200 disabled:cursor-not-allowed p-0.5"
                        title="Move down"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Inline Exercise Editor */}
              {isExpanded && (
                <div className="mt-4">
                  {USE_LOCAL_FIRST_WORKOUT && dayId ? (
                    <ExerciseCard
                      exercise={exercise}
                      setsData={workoutDraft.getExerciseSets(exercise.exercise_id)}
                      onUpdateSet={(setNum, data) => workoutDraft.updateSet(exercise.exercise_id, setNum, data)}
                      onToggleCompletion={(setNum) => workoutDraft.toggleCompletion(exercise.exercise_id, setNum)}
                      onExerciseComplete={handleComplete}
                      onUncompleteExercise={() => handleUncompleteExercise(exercise)}
                      onAddSet={() => handleAddSet(exercise)}
                      onDeleteSet={(setNum) => handleDeleteSet(exercise, setNum)}
                      syncBeforeComplete={workoutDraft.syncNow}
                      readOnly={readOnly}
                      forceExpanded={true}
                    />
                  ) : (
                    <ExerciseTracker
                      exercise={exercise}
                      onComplete={handleComplete}
                      readOnly={readOnly}
                      forceExpanded={true}
                      onProgressUpdate={(completed, total) =>
                        handleExerciseProgressUpdate(exercise.exercise_id, completed, total)
                      }
                    />
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Add Exercise Button - only show if not readOnly and workoutId exists */}
      {!readOnly && workoutId && (
        <div className="mt-4 px-4 pb-4">
          {isAddingExercise ? (
            <div className="border rounded-lg p-4 bg-gray-50">
              <h3 className="font-medium mb-3">Add Exercise</h3>
              <ExerciseSelector 
                onSelect={setSelectedExerciseType} 
                selectedExercise={selectedExerciseType} 
                userId={userIdForExercises}
              />
              <div className="flex justify-end space-x-2 mt-4">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setIsAddingExercise(false);
                    setSelectedExerciseType('');
                  }}
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  disabled={!selectedExerciseType}
                  onClick={handleAddExercise}
                >
                  Add Exercise
                </Button>
              </div>
            </div>
          ) : (
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsAddingExercise(true)}
              className="w-full"
            >
              Add Exercise
            </Button>
          )}
        </div>
      )}

    </>
  );
};

export default ExerciseList;