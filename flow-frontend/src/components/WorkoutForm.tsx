import { useState, useEffect } from 'react';
import ExerciseSelector from './ExerciseSelector';
import FormButton from './FormButton';
import { createWorkout } from '../services/api';
import { fetchAuthSession } from 'aws-amplify/auth';
import { useWeightUnit } from '../contexts/UserContext';

// Define a single set configuration with optional weight
interface SetConfig {
  id: string; // Unique identifier
  reps: number;
  rpe: number;
  weight?: number; // Optional weight field for planning
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
  athleteId?: string;
}

const WorkoutForm = ({ dayId, onSave, athleteId }: WorkoutFormProps) => {
  const [selectedExercise, setSelectedExercise] = useState<string>('');
  const [exercises, setExercises] = useState<ExerciseConfig[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string>();
  
  // Add weight unit context
  const { getDisplayUnit } = useWeightUnit();
  
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

  // State for exercise configuration
  const [isConfiguring, setIsConfiguring] = useState(false);
  
  // State for set management with enhanced default including weight
  const [currentSets, setCurrentSets] = useState<SetConfig[]>([
    { id: '1', reps: 5, rpe: 7, weight: 0 }
  ]);

  // Generate a unique ID for sets
  const generateSetId = () => {
    return Math.random().toString(36).substring(2, 11);
  };

  const handleAddExercise = () => {
    if (!selectedExercise) return;
    
    // Reset current sets to a default single set with weight
    setCurrentSets([{ 
      id: '1', 
      reps: 5, 
      rpe: 7, 
      weight: 0 
    }]);
    
    // Start configuring this exercise
    setIsConfiguring(true);
  };

  const handleAddSet = () => {
    // Get the last set's values to use as defaults for the new set
    const lastSet = currentSets[currentSets.length - 1];

    // Add a new set with default values including weight
    const newSet: SetConfig = {
      id: generateSetId(),
      reps: lastSet.reps,
      rpe: lastSet.rpe,
      weight: lastSet.weight,
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

  // Enhanced format exercise for display with improved weight formatting
  const formatExerciseDisplay = (exercise: ExerciseConfig) => {
    const displayUnit = getDisplayUnit(exercise.exerciseType);
    
    // Check if all sets have same configuration
    const allSameReps = exercise.sets.every(set => set.reps === exercise.sets[0].reps);
    const allSameRPE = exercise.sets.every(set => set.rpe === exercise.sets[0].rpe);
    const allSameWeight = exercise.sets.every(set => (set.weight || 0) === (exercise.sets[0].weight || 0));
    
    // For uniform sets - Format: "120kg - 3 sets × 5 reps @ RPE 7" or "3 sets × 5 reps @ RPE 7" if no weight
    if (allSameReps && allSameRPE && allSameWeight) {
      const weight = exercise.sets[0].weight || 0;
      const weightPrefix = weight > 0 ? `${weight}${displayUnit} - ` : '';
      const repsText = allSameReps ? `${exercise.sets[0].reps} reps` : 'varied reps';
      return `${weightPrefix}${exercise.sets.length} sets × ${repsText} @ RPE ${exercise.sets[0].rpe}`;
    }
    
    // For varied sets, group similar ones together
    const groups: Record<string, number[]> = {};
    
    exercise.sets.forEach((set, index) => {
      const setIndex = index + 1; // 1-based index for display
      const key = `${set.reps}_${set.rpe}_${set.weight || 0}`; // Include weight in key
      
      if (!groups[key]) {
        groups[key] = [];
      }
      
      groups[key].push(setIndex);
    });
    
    // Now format the groups
    const setDescriptions = Object.entries(groups).map(([key, indices]) => {
      const [reps, rpe, weight] = key.split('_');
      const weightNum = parseFloat(weight);
      
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
      
      // Format: "120kg - Set 1: 5 reps @ RPE 7" or "Set 1: 5 reps @ RPE 7" if no weight
      const weightPrefix = weightNum > 0 ? `${weightNum}${displayUnit} - ` : '';
      return `${weightPrefix}${setLabel}: ${reps} reps @ RPE ${rpe}`;
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
          weight: exercise.sets[0].weight || 0, // Use planned weight or default to 0
          rpe: exercise.sets[0].rpe, // Default RPE from first set
          notes: '',
          // Transform sets data to match the backend model
          sets_data: exercise.sets.map((set, index) => ({
            set_number: index + 1,
            reps: set.reps,
            weight: set.weight || 0, // Include planned weight
            rpe: set.rpe,
            completed: false
          }))
        };
        
        console.log('Formatted exercise with weights:', exerciseData);
        return exerciseData;
      });
      
      console.log('Saving workout for day:', dayId);
      console.log('Formatted exercises to save:', formattedExercises);
      
      // Create workout with properly formatted data including weights
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

  // Enhanced set configuration UI with weight fields
  const renderSetConfiguration = () => {
    if (!isConfiguring) return null;
    
    const displayUnit = getDisplayUnit(selectedExercise);
    
    return (
      <div className="border rounded p-4 bg-white">
        <h3 className="font-medium mb-3">Configure {selectedExercise}</h3>
        
        <div className="space-y-4">
          {currentSets.map((set, index) => (
            <div key={set.id} className="flex items-center space-x-2 sm:space-x-4 p-2 bg-gray-50 rounded">
              <div className="font-medium min-w-8 text-sm">Set {index + 1}</div>
              
              <div className="flex-shrink-0">
                <label className="block text-xs text-gray-500">Weight ({displayUnit})</label>
                <input
                  type="number"
                  inputMode="decimal"
                  step="0.5"
                  defaultValue={set.weight || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '' || value === '0') {
                      handleUpdateSet(set.id, 'weight', 0);
                    } else {
                      handleUpdateSet(set.id, 'weight', Math.max(0, parseFloat(value) || 0));
                    }
                  }}
                  onFocus={(e) => e.target.select()}
                  className="w-16 sm:w-20 p-1 border rounded text-center text-sm"
                  placeholder="0"
                />
              </div>
              
              <div className="flex-shrink-0">
                <label className="block text-xs text-gray-500">Reps</label>
                <input
                  type="number"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  defaultValue={set.reps}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '') {
                      handleUpdateSet(set.id, 'reps', 1);
                    } else {
                      handleUpdateSet(set.id, 'reps', Math.max(1, parseInt(value) || 1));
                    }
                  }}
                  onFocus={(e) => e.target.select()}
                  className="w-12 sm:w-16 p-1 border rounded text-center text-sm"
                />
              </div>
              
              <div className="flex-shrink-0">
                <label className="block text-xs text-gray-500">RPE</label>
                <input
                  type="number"
                  inputMode="decimal"
                  step="0.5"
                  defaultValue={set.rpe}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '') {
                      handleUpdateSet(set.id, 'rpe', 1);
                    } else {
                      handleUpdateSet(set.id, 'rpe', Math.min(10, Math.max(1, parseFloat(value) || 1)));
                    }
                  }}
                  onFocus={(e) => e.target.select()}
                  className="w-12 sm:w-16 p-1 border rounded text-center text-sm"
                />
              </div>
              
              <button
                onClick={() => handleRemoveSet(set.id)}
                className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                disabled={currentSets.length <= 1}
                title="Remove set"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
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
    );
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
              <li key={index} className="py-3 flex items-start space-x-2 sm:space-x-4">
                <div className="flex-1 min-w-0">
                  <p className="font-medium mb-1 text-sm">{exercise.exerciseType}</p>
                  {formatExerciseDisplay(exercise).split('\n').map((line, i) => (
                    <p key={i} className="text-xs text-gray-600 break-words">{line}</p>
                  ))}
                </div>
                <button
                  onClick={() => handleRemoveExercise(index)}
                  className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 flex-shrink-0 mt-0.5"
                  title="Remove exercise"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Enhanced Set Configuration UI */}
      {renderSetConfiguration()}
      
      {/* Exercise selector and action buttons - only show when not configuring */}
      {!isConfiguring && (
        <>
          <ExerciseSelector 
            onSelect={setSelectedExercise} 
            selectedExercise={selectedExercise}
            userId={userIdForExercises}
          />
          
          {/* Exercise management section */}
          <div className="flex justify-start">
            <FormButton
              onClick={handleAddExercise}
              disabled={!selectedExercise}
              type="button"
              variant="secondary"
            >
              Add Exercise
            </FormButton>
          </div>
          
          {/* Workout save section - separated with visual gap */}
          {exercises.length > 0 && (
            <div className="mt-6 pt-4 border-t border-gray-200">
              <div className="flex justify-center">
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
          )}
        </>
      )}
    </div>
  );
};

export default WorkoutForm;