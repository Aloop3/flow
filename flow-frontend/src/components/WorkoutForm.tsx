import { useState } from 'react';
import ExerciseSelector from './ExerciseSelector';
import FormButton from './FormButton';
import { createWorkout } from '../services/api';

// Define a single set configuration
interface SetConfig {
  id: string; // Unique identifier
  reps: number;
  rpe: number;
}

// Define the exercise with sets
interface ExerciseConfig {
  exerciseType: string;
  sets: SetConfig[];
  status?: 'planned' | 'completed' | 'skipped';
}

interface WorkoutFormProps {
  dayId: string;
  onSave: (workoutId: string) => void;
}

const WorkoutForm = ({ dayId, onSave }: WorkoutFormProps) => {
  const [selectedExercise, setSelectedExercise] = useState<string>('');
  const [exercises, setExercises] = useState<ExerciseConfig[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // State for exercise configuration
  const [isConfiguring, setIsConfiguring] = useState(false);
  
  // State for set management
  const [currentSets, setCurrentSets] = useState<SetConfig[]>([
    { id: '1', reps: 5, rpe: 7 }
  ]);

  // Generate a unique ID for sets
  const generateSetId = () => {
    return Math.random().toString(36).substr(2, 9);
  };

  const handleAddExercise = () => {
    if (!selectedExercise) return;
    
    // Reset current sets to a default single set
    setCurrentSets([{ id: '1', reps: 5, rpe: 7 }]);
    
    // Start configuring this exercise
    setIsConfiguring(true);
  };

  const handleAddSet = () => {
    // Add a new set with default values
    const newSet: SetConfig = {
      id: generateSetId(),
      reps: 5,
      rpe: 7
    };
    
    setCurrentSets([...currentSets, newSet]);
  };

  const handleRemoveSet = (id: string) => {
    // Don't allow removing the last set
    if (currentSets.length <= 1) return;
    
    setCurrentSets(currentSets.filter(set => set.id !== id));
  };

  const handleUpdateSet = (id: string, field: keyof Omit<SetConfig, 'id'>, value: number) => {
    setCurrentSets(currentSets.map(set => 
      set.id === id ? { ...set, [field]: value } : set
    ));
  };

  const handleSaveExercise = () => {
    const newExercise: ExerciseConfig = {
      exerciseType: selectedExercise,
      sets: currentSets,
      status: 'planned'
    };
    
    setExercises([...exercises, newExercise]);
    setIsConfiguring(false);
    setSelectedExercise('');
  };

  const handleCancelExercise = () => {
    setIsConfiguring(false);
    setSelectedExercise('');
  };

  const handleRemoveExercise = (index: number) => {
    setExercises(prev => prev.filter((_, i) => i !== index));
  };

  // Format exercise for display
  const formatExerciseDisplay = (exercise: ExerciseConfig) => {
    // Check if all sets have same reps and RPE
    const allSameReps = exercise.sets.every(set => set.reps === exercise.sets[0].reps);
    const allSameRPE = exercise.sets.every(set => set.rpe === exercise.sets[0].rpe);
    
    // For uniform sets
    if (allSameReps && allSameRPE) {
      return `${exercise.sets.length} sets × ${exercise.sets[0].reps} reps @ RPE ${exercise.sets[0].rpe}`;
    }
    
    // For varied sets, group similar ones together
    // First, create a unique key for each set configuration
    const groups: Record<string, number[]> = {};
    
    exercise.sets.forEach((set, index) => {
      const setIndex = index + 1; // 1-based index for display
      const key = `${set.reps}_${set.rpe}`; // Create key from reps and RPE
      
      if (!groups[key]) {
        groups[key] = [];
      }
      
      groups[key].push(setIndex);
    });
    
    // Now format the groups
    const setDescriptions = Object.entries(groups).map(([key, indices]) => {
      const [reps, rpe] = key.split('_');
      
      // Format the set numbers (e.g., "Set 1" or "Sets 2-4")
      let setLabel: string;
      if (indices.length === 1) {
        setLabel = `Set ${indices[0]}`;
      } else {
        // Check if indices are consecutive
        const isConsecutive = indices.every((val, i, arr) => 
          i === 0 || val === arr[i-1] + 1
        );
        
        if (isConsecutive) {
          setLabel = `Sets ${indices[0]}-${indices[indices.length - 1]}`;
        } else {
          setLabel = `Sets ${indices.join(', ')}`;
        }
      }
      
      return `${setLabel}: ${reps} reps @ RPE ${rpe}`;
    });
    
    // Join the set descriptions with line breaks for better readability
    return setDescriptions.join('\n');
  };

  
  const handleSaveWorkout = async () => {
    if (exercises.length === 0) {
      setError("Please add at least one exercise first");
      return;
    }
    
    setIsSaving(true);
    setError(null);
    
    try {
      // Transform exercises to the format expected by the backend
      const formattedExercises = exercises.map(exercise => {
        // Create the exercise object with required fields
        const exerciseData = {
          exerciseType: exercise.exerciseType,
          sets: exercise.sets.length,
          reps: exercise.sets[0].reps, // Default reps from first set
          weight: 0, // Set to 0 as per RPE-based requirements
          rpe: exercise.sets[0].rpe, // Default RPE from first set
          notes: '',
          // Transform sets data to match the backend model
          sets_data: exercise.sets.map((set, index) => ({
            set_number: index + 1,
            reps: set.reps,
            weight: 0, // Weight is 0 for RPE-based training
            rpe: set.rpe,
            completed: false
          }))
        };
        
        console.log('Formatted exercise:', exerciseData);
        return exerciseData;
      });
      
      console.log('Saving workout for day:', dayId);
      console.log('Formatted exercises to save:', formattedExercises);
      
      // Create workout with properly formatted data
      const workout = await createWorkout(dayId, formattedExercises);
      
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
              <li key={index} className="py-3 flex justify-between items-start">
                <div>
                  <p className="font-medium mb-1">{exercise.exerciseType}</p>
                  {formatExerciseDisplay(exercise).split('\n').map((line, i) => (
                    <p key={i} className="text-sm text-gray-600">{line}</p>
                  ))}
                </div>
                <button
                  onClick={() => handleRemoveExercise(index)}
                  className="text-red-500 hover:text-red-700 mt-1"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {isConfiguring ? (
        <div className="border rounded p-4 bg-white">
          <h3 className="font-medium mb-3">Configure {selectedExercise}</h3>
          
          <div className="space-y-4">
            {currentSets.map((set, index) => (
              <div key={set.id} className="flex items-center space-x-4 p-2 bg-gray-50 rounded">
                <div className="font-medium min-w-10">Set {index + 1}</div>
                
                <div>
                  <label className="block text-xs text-gray-500">Reps</label>
                  <input
                    type="number"
                    value={set.reps}
                    onChange={(e) => handleUpdateSet(set.id, 'reps', Math.max(1, parseInt(e.target.value) || 1))}
                    className="w-16 p-1 border rounded"
                    min="1"
                  />
                </div>
                
                <div>
                  <label className="block text-xs text-gray-500">RPE</label>
                  <input
                    type="number"
                    value={set.rpe}
                    onChange={(e) => handleUpdateSet(set.id, 'rpe', Math.min(10, Math.max(1, parseFloat(e.target.value) || 1)))}
                    className="w-16 p-1 border rounded"
                    min="1"
                    max="10"
                    step="0.5"
                  />
                </div>
                
                <button
                  onClick={() => handleRemoveSet(set.id)}
                  className="text-red-500 hover:text-red-700 ml-auto"
                  disabled={currentSets.length <= 1}
                >
                  Remove
                </button>
              </div>
            ))}
            
            <button
              onClick={handleAddSet}
              className="flex items-center text-blue-600 hover:text-blue-800"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Set
            </button>
            
            <div className="flex justify-end space-x-2 pt-4 border-t mt-4">
              <button
                onClick={handleCancelExercise}
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveExercise}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Add Exercise
              </button>
            </div>
          </div>
        </div>
      ) : (
        <>
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
        </>
      )}
    </div>
  );
};

export default WorkoutForm;