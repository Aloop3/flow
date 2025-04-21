import { useState } from 'react';
import ExerciseSelector from './ExerciseSelector';
import FormButton from './FormButton';
import { createWorkout } from '../services/api';


interface WorkoutFormProps {
  dayId: string;
  onSave: (workoutId: string) => void;
}

const WorkoutForm = ({ dayId, onSave }: WorkoutFormProps) => {
  const [selectedExercise, setSelectedExercise] = useState<string>('');
  const [exercises, setExercises] = useState<Array<{
    exerciseType: string;
    sets: number;
    reps: number;
    weight: number;
    status?: 'planned' | 'completed' | 'skipped';
  }>>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddExercise = () => {
    if (!selectedExercise) return;
    
    setExercises(prev => [
      ...prev, 
      {
        exerciseType: selectedExercise,
        sets: 3,
        reps: 10,
        weight: 0,
        status: 'planned'
      }
    ]);
    
    setSelectedExercise('');
  };

  const handleRemoveExercise = (index: number) => {
    setExercises(prev => prev.filter((_, i) => i !== index));
  };

  const handleSaveWorkout = async () => {
    if (exercises.length === 0) {
      setError("Please add at least one exercise first");
      return;
    }
    
    setIsSaving(true);
    setError(null);
    
    try {
      console.log('Saving workout for day:', dayId);
      console.log('Exercises to save:', exercises);
      
      // Use the API method directly
      const workout = await createWorkout(dayId, exercises);
      
      console.log('Created workout:', workout);
      
      // Call the onSave callback with the workout ID
      if (workout && workout.workout_id) {
        onSave(workout.workout_id);
      } else {
        console.error('No workout ID returned');
        setError('Failed to create workout - no ID returned');
      }
    } catch (error: any) {
      console.error('Error saving workout:', error);
      setError(error.message || 'Failed to save workout');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-medium">Create Workout</h2>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}
      
      {exercises.length > 0 && (
        <div className="border rounded p-4 bg-gray-50">
          <h3 className="text-md font-medium mb-2">Exercises</h3>
          <ul className="divide-y">
            {exercises.map((exercise, index) => (
              <li key={index} className="py-2 flex justify-between items-center">
                <div>
                  <p className="font-medium">{exercise.exerciseType}</p>
                  <p className="text-sm text-gray-600">
                    {exercise.sets} sets × {exercise.reps} reps @ {exercise.weight} lbs
                  </p>
                </div>
                <button
                  onClick={() => handleRemoveExercise(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Exercise selector */}
      <ExerciseSelector 
        onSelect={setSelectedExercise} 
        selectedExercise={selectedExercise} 
      />
      
      {/* Add exercise button */}
      <div className="flex justify-between">
        <FormButton
          onClick={handleAddExercise}
          disabled={!selectedExercise}
          type="button"
          variant="secondary"
        >
          Add Exercise
        </FormButton>

        <FormButton
          onClick={handleSaveWorkout}
          disabled={exercises.length === 0 || isSaving}
          type="button"
          variant="primary"
          isLoading={isSaving}
        >
          Save Workout
        </FormButton>
      </div>
    </div>
  );
};

export default WorkoutForm;