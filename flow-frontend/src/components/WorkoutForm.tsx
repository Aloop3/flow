import { useState } from 'react';
import ExerciseSelector from './ExerciseSelector';
import FormButton from './FormButton';
import { getAuthHeaders } from '../services/api';
import { post } from 'aws-amplify/api';

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
        weight: 0
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
      
      // Get auth headers
      const headers = await getAuthHeaders();
      
      // Send request to create workout
      const apiResponse = await post({
        apiName: 'flow-api',
        path: `/days/${dayId}/workout`,
        options: {
          headers,
          body: {
            exercises: exercises
          }
        }
      });
      
      console.log('Initial API response:', apiResponse);
      
      // For Amplify v6, await the response
      const actualResponse = await apiResponse.response;
      console.log('Actual response after awaiting:', actualResponse);
      
      // Check if request was successful
      if (actualResponse.statusCode >= 200 && actualResponse.statusCode < 300) {
        // Parse response body
        if (actualResponse.body) {
          try {
            const responseText = await actualResponse.body.text();
            console.log('Response text:', responseText);
            
            if (responseText) {
              const data = JSON.parse(responseText);
              console.log('Parsed workout data:', data);
              
              if (data && data.workout_id) {
                // Successfully created workout
                onSave(data.workout_id);
                return;
              } else {
                console.error('No workout_id in response:', data);
                setError('Server returned invalid response (missing workout ID)');
              }
            }
          } catch (parseError) {
            console.error('Error parsing response:', parseError);
            setError('Failed to parse server response');
          }
        } else {
          console.error('No response body');
          setError('Server returned empty response');
        }
      } else {
        // Handle HTTP error
        let errorMessage = `Server returned status ${actualResponse.statusCode}`;
        
        try {
          if (actualResponse.body) {
            const errorText = await actualResponse.body.text();
            if (errorText) {
              const errorData = JSON.parse(errorText);
              if (errorData && errorData.error) {
                errorMessage = errorData.error;
              }
            }
          }
        } catch (e) {
          // Ignore error parsing errors
        }
        
        console.error('HTTP error:', errorMessage);
        setError(errorMessage);
      }
      
      // If we get here, there was an issue
      onSave('');
    } catch (error: any) {
      console.error('Error saving workout:', error);
      setError(error.message || 'Unknown error occurred');
      onSave('');
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