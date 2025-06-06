import { useState, useEffect } from 'react';
import type { Exercise } from '../services/api';
import { createExercise, deleteExercise } from '../services/api';
import ExerciseTracker from './ExerciseTracker';
import ExerciseSelector from './ExerciseSelector';
import Modal from './Modal';
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
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [isAddingExercise, setIsAddingExercise] = useState(false);
  const [selectedExerciseType, setSelectedExerciseType] = useState<string>('');
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string>();
  
  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'skipped':
        return 'bg-gray-100 text-gray-800';
      case 'planned':
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

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

  // Use athleteId when provided (coach context), otherwise current user
  const userIdForExercises = athleteId || userId;

  const handleExerciseClick = (exercise: Exercise) => {
    if (!readOnly) {
      setSelectedExercise(exercise);
    }
  };

  const handleComplete = () => {
    setSelectedExercise(null);
    onExerciseComplete();
  };

  const handleAddExercise = async () => {
    if (!selectedExerciseType || !workoutId) return;
    
    try {
      setError(null);
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
    } catch (err: any) {
      setError('Failed to add exercise. Please try again.');
      console.error('Error adding exercise:', err);
    }
  };

  const handleRemoveExercise = async (exerciseId: string) => {
    try {
      setIsDeleting(exerciseId);
      setError(null);
      
      await deleteExercise(exerciseId);
      
      // Refresh the workout data
      onExerciseComplete();
    } catch (err: any) {
      setError('Failed to remove exercise. Please try again.');
      console.error('Error removing exercise:', err);
    } finally {
      setIsDeleting(null);
    }
  };

  // Calculate progress for sets
  const getSetProgress = (exercise: Exercise) => {
    if (!exercise.sets_data || exercise.sets_data.length === 0) {
      return { completed: 0, total: exercise.sets };
    }
    
    const completedSets = exercise.sets_data.filter(set => set.completed).length;
    return { 
      completed: completedSets, 
      total: exercise.sets
    };
  };

  return (
    <>
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}
      
      <ul className="divide-y">
        {exercises.map((exercise) => {
          const setProgress = getSetProgress(exercise);
          const hasSetData = exercise.sets_data && exercise.sets_data.length > 0;
          
          return (
            <li 
              key={exercise.exercise_id} 
              className={`py-3 flex justify-between items-start ${
                !readOnly && exercise.status !== 'completed' ? 'cursor-pointer hover:bg-gray-50' : ''
              }`}
            >
              <div 
                className="flex-grow"
                onClick={() => handleExerciseClick(exercise)}
              >
                <div className="flex justify-between items-center mb-1">
                  <h3 className="font-medium">{exercise.exercise_type}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(exercise.status)}`}>
                    {exercise.status || 'planned'}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600">
                  {exercise.sets} sets × {exercise.reps} reps
                  {exercise.rpe && ` @ RPE ${exercise.rpe}`}
                </p>
                
                {exercise.notes && (
                  <p className="mt-1 text-xs text-gray-500">{exercise.notes}</p>
                )}
                
                {/* Set progress bar */}
                {hasSetData && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Set progress</span>
                      <span>{setProgress.completed} / {setProgress.total} sets</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(setProgress.completed / setProgress.total) * 100}%` }}
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
            </li>
          );
        })}
      </ul>
      
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

      <Modal
        isOpen={!!selectedExercise}
        onClose={() => setSelectedExercise(null)}
        title={selectedExercise ? `${selectedExercise.exercise_type}` : 'Exercise Details'}
      >
        {selectedExercise && (
          <ExerciseTracker
            exercise={selectedExercise}
            onComplete={handleComplete}
            onCancel={() => setSelectedExercise(null)}
          />
        )}
      </Modal>
    </>
  );
};

export default ExerciseList;
