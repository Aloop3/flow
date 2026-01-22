import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { completeExercise } from '../services/api';
import type { Exercise } from '../services/api';
import SetTracker from './SetTracker';

interface ExerciseCompletionProps {
  exercise: Exercise;
  onComplete: () => void;
  onCancel: () => void;
}

const ExerciseCompletion = ({ exercise, onComplete, onCancel }: ExerciseCompletionProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [localExercise, setLocalExercise] = useState<Exercise>(exercise);
  const [allSetsCompleted, setAllSetsCompleted] = useState(false);

  // Check if all sets are completed when sets_data changes
  useEffect(() => {
    if (localExercise.sets_data && localExercise.sets_data.length > 0) {
      const completedSets = localExercise.sets_data.filter(set => set.completed).length;
      setAllSetsCompleted(completedSets >= localExercise.sets);
    } else {
      setAllSetsCompleted(false);
    }
  }, [localExercise.sets_data, localExercise.sets]);

  // Update localExercise when the parent exercise changes
  useEffect(() => {
    setLocalExercise(exercise);
  }, [exercise]);

  const handleSetTracked = async () => {
    // Refresh the exercise data
    onComplete();
    
    // Update the local exercise data
    if (exercise.sets_data) {
      setLocalExercise(prev => ({
        ...prev,
        sets_data: [...(exercise.sets_data || [])]
      }));
    }
  };

  const handleQuickComplete = async () => {
    setIsLoading(true);
    setError(null);
  
    try {
      // Create a completion object based only on tracked sets
      // (sets that exist in the backend)
      const trackedSets = localExercise.sets_data?.filter(set => set.completed) || [];
      const setCount = trackedSets.length || localExercise.sets;
      
      // Use the data from tracked sets if available
      const completionData = {
        // Use the actual number of completed sets, not the local count
        sets: setCount,
        reps: localExercise.reps, 
        weight: localExercise.weight,
        rpe: localExercise.rpe,
        status: allSetsCompleted ? 'completed' as 'completed' : 'planned' as 'planned',
        notes: localExercise.notes
      };
  
      await completeExercise(exercise.exercise_id, completionData);
      onComplete();
    } catch (err: any) {
      console.error('Error completing exercise:', err);
      setError(err.message || 'Failed to complete exercise');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* <h3 className="text-lg font-medium">{exercise.exercise_type}</h3> */}
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <SetTracker 
        exerciseId={exercise.exercise_id}
        exerciseType={exercise.exercise_type}
        plannedSets={exercise.sets}
        plannedReps={exercise.reps}
        plannedWeight={exercise.weight}
        existingSetsData={localExercise.sets_data}
        onSetTracked={handleSetTracked}
      />
      
      {/* Show mark exercise complete button if sets are logged */}
      {localExercise.sets_data && localExercise.sets_data.length > 0 && (
        <div className="flex justify-end mt-4 pt-3 border-t">
          <Button
            type="button"
            disabled={isLoading}
            onClick={handleQuickComplete}
          >
            {isLoading ? 'Saving...' : (allSetsCompleted ? "Update Exercise" : "Mark Exercise Complete")}
          </Button>
        </div>
      )}

      {/* Cancel button */}
      <div className="flex justify-end mt-4">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Close
        </Button>
      </div>
    </div>
  );
};

export default ExerciseCompletion;