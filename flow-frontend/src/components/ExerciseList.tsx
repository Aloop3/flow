import { useState, useEffect } from 'react';
import type { Exercise } from '../services/api';
import { createExercise, deleteExercise } from '../services/api';
import ExerciseTracker from './ExerciseTracker';
import ExerciseSelector from './ExerciseSelector';
import FormButton from './FormButton';
import { fetchAuthSession } from 'aws-amplify/auth';

interface ExerciseListProps {
  exercises: Exercise[];
  workoutId?: string;
  onExerciseComplete: () => void;
  readOnly?: boolean;
  athleteId?: string;
}

const ExerciseList = ({ athleteId, exercises, workoutId, onExerciseComplete, readOnly = false }: ExerciseListProps) => {
  const [expandedExerciseId, setExpandedExerciseId] = useState<string | null>(null);
  const [isAddingExercise, setIsAddingExercise] = useState(false);
  const [selectedExerciseType, setSelectedExerciseType] = useState<string>('');
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string>();
  
  // Local progress tracking for instant updates
  const [localProgressMap, setLocalProgressMap] = useState<Record<string, { completed: number; total: number }>>({});

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
    } catch (err: any) {
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
    } catch (err: any) {
      setError('Failed to remove exercise. Please try again.');
      console.error('Error removing exercise:', err);
    } finally {
      setIsDeleting(null);
    }
  };

  // Get set progress with local progress fallback for instant updates
  const getSetProgress = (exercise: Exercise) => {
    // Use local progress if available, otherwise calculate from exercise data
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
      
      <div className="divide-y">
        {exercises.map((exercise) => {
          const setProgress = getSetProgress(exercise);
          const hasSetData = exercise.sets_data && exercise.sets_data.length > 0;
          const isExpanded = expandedExerciseId === exercise.exercise_id;
          
          return (
            <div key={exercise.exercise_id} className="py-3">
              {/* Exercise Summary Row */}
              <div className={`flex justify-between items-start ${
                !readOnly && exercise.status !== 'completed' ? 'cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors' : ''
              }`}>
                <div 
                  className="flex-grow"
                  onClick={() => handleExerciseClick(exercise)}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="font-medium">{exercise.exercise_type}</h3>
                    {/* Expansion indicator */}
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
                  
                  <p className="text-sm text-gray-600">
                    {exercise.sets} sets × {exercise.reps} reps
                    {exercise.rpe && ` @ RPE ${exercise.rpe}`}
                  </p>
                  
                  {exercise.notes && (
                    <p className="mt-1 text-xs text-gray-500">{exercise.notes}</p>
                  )}
                  
                  {/* Set progress bar - uses local progress for instant updates */}
                  {(hasSetData || setProgress.completed > 0) && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Set progress</span>
                        <span>{setProgress.completed} / {setProgress.total} sets</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${setProgress.total > 0 ? (setProgress.completed / setProgress.total) * 100 : 0}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Remove button - only show if not readOnly and workoutId exists */}
                {!readOnly && workoutId && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveExercise(exercise.exercise_id);
                    }}
                    disabled={isDeleting === exercise.exercise_id}
                    className="ml-4 text-red-500 hover:text-red-700 disabled:text-gray-400"
                    title="Remove exercise"
                  >
                    {isDeleting === exercise.exercise_id ? (
                      <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    )}
                  </button>
                )}
              </div>

              {/* Inline ExerciseTracker */}
              {isExpanded && (
                <div className="mt-4 ml-2">
                  <ExerciseTracker
                    exercise={exercise}
                    onComplete={handleComplete}
                    readOnly={readOnly}
                    forceExpanded={true}
                    onProgressUpdate={(completed, total) => 
                      handleExerciseProgressUpdate(exercise.exercise_id, completed, total)
                    }
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Add Exercise Button - only show if not readOnly and workoutId exists */}
      {!readOnly && workoutId && (
        <div className="mt-4">
          {isAddingExercise ? (
            <div className="border rounded-lg p-4 bg-gray-50">
              <h3 className="font-medium mb-3">Add Exercise</h3>
              <ExerciseSelector 
                onSelect={setSelectedExerciseType} 
                selectedExercise={selectedExerciseType} 
                userId={userIdForExercises}
              />
              <div className="flex justify-end space-x-2 mt-4">
                <FormButton
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setIsAddingExercise(false);
                    setSelectedExerciseType('');
                  }}
                >
                  Cancel
                </FormButton>
                <FormButton
                  type="button"
                  variant="primary"
                  disabled={!selectedExerciseType}
                  onClick={handleAddExercise}
                >
                  Add Exercise
                </FormButton>
              </div>
            </div>
          ) : (
            <FormButton
              type="button"
              variant="secondary"
              onClick={() => setIsAddingExercise(true)}
              className="w-full"
            >
              Add Exercise
            </FormButton>
          )}
        </div>
      )}

    </>
  );
};

export default ExerciseList;