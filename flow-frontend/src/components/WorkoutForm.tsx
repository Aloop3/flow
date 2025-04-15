import { useState } from 'react';
import ExerciseSelector from './ExerciseSelector';
import FormButton from './FormButton';

interface WorkoutFormProps {
  dayId: string;
  onSave: () => void;
}

const WorkoutForm = ({ dayId, onSave }: WorkoutFormProps) => {
  const [selectedExercise, setSelectedExercise] = useState<string>('');
  const [exercises, setExercises] = useState<Array<{
    exerciseType: string;
    sets: number;
    reps: number;
    weight: number;
  }>>([]);
  const [isSaving, setIsSaving] = useState(false);

  const handleAddExercise = () => {
    if (!selectedExercise) return;
    
    setExercises(prev => [
      ...prev, 
      {
        exerciseType: selectedExercise,
        sets: 3,
        reps: 10,
        weight: 0
      }
    ]);
    
    setSelectedExercise('');
  };

  const handleSaveWorkout = async () => {
    if (exercises.length === 0) return;
    
    setIsSaving(true);
    try {
      // Here you would typically call an API to save the workout
      // For example: await createWorkout(dayId, exercises);
      
      // Call the onSave callback to notify parent component
      onSave();
    } catch (error) {
      console.error('Error saving workout:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-medium">Create Workout</h2>
      
      {/* Added exercises */}
      {exercises.length > 0 && (
        <div className="border rounded p-4 bg-gray-50">
          <h3 className="text-md font-medium mb-2">Planned Exercises</h3>
          <ul className="divide-y">
            {exercises.map((exercise, index) => (
              <li key={index} className="py-2">
                <p className="font-medium">{exercise.exerciseType}</p>
                <p className="text-sm text-gray-600">
                  {exercise.sets} sets × {exercise.reps} reps @ {exercise.weight} lbs
                </p>
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