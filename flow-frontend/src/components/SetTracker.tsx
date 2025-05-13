import { useState, useEffect } from 'react';
import { trackExerciseSet, deleteSet } from '../services/api';
import FormButton from './FormButton';
import type { ExerciseSetData } from '../services/api';

interface SetTrackerProps {
  exerciseId: string;
  exerciseType: string;
  plannedSets: number;
  plannedReps: number;
  plannedWeight: number;
  existingSetsData?: ExerciseSetData[];
  onSetTracked: () => void;
}

const SetTracker = ({
  exerciseId,
  exerciseType,
  plannedSets = 1,
  plannedReps = 0,
  plannedWeight = 0,
  existingSetsData = [],
  onSetTracked
}: SetTrackerProps) => {
  // Validate inputs to prevent rendering issues
  const validExerciseId = exerciseId || '';
  const validExerciseType = exerciseType || 'Exercise';
  const validPlannedSets = Math.max(1, plannedSets); // Ensure at least 1 set
  const validPlannedReps = Math.max(0, plannedReps);
  const validPlannedWeight = Math.max(0, plannedWeight);

  // Track the actual number of sets (can be different from planned)
  const [actualSets, setActualSets] = useState<number>(validPlannedSets);
  const [activeSetNumber, setActiveSetNumber] = useState<number | null>(null);
  const [setData, setSetData] = useState({
    reps: validPlannedReps,
    weight: validPlannedWeight,
    rpe: undefined as number | undefined,
    notes: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize actual sets based on existing data
  useEffect(() => {
    if (existingSetsData && existingSetsData.length > 0) {
      const maxSetNumber = Math.max(
        ...existingSetsData.map(set => set.set_number || 0),
        validPlannedSets
      );
      setActualSets(maxSetNumber);
    } else {
      setActualSets(validPlannedSets);
    }
  }, [existingSetsData, validPlannedSets]);

  // Generate array of set numbers based on actual sets
  const sets = Array.from({ length: actualSets }, (_, i) => i + 1);

  // Map existing set data by set number for quick lookup
  const setsDataMap = (existingSetsData || []).reduce((map, setData) => {
    if (setData && typeof setData.set_number === 'number') {
      map[setData.set_number] = setData;
    }
    return map;
  }, {} as Record<number, ExerciseSetData>);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setSetData(prev => ({
      ...prev,
      [name]: name === 'notes' ? value : Number(value) || 0
    }));
  };

  const selectSet = (setNumber: number) => {
    // If this set already has data, pre-fill the form
    if (setsDataMap[setNumber]) {
      const existingData = setsDataMap[setNumber];
      setSetData({
        reps: existingData.reps || validPlannedReps,
        weight: existingData.weight || validPlannedWeight,
        rpe: existingData.rpe,
        notes: existingData.notes || '',
      });
    } else {
      // Otherwise use planned values
      setSetData({
        reps: validPlannedReps,
        weight: validPlannedWeight,
        rpe: undefined,
        notes: '',
      });
    }
    setActiveSetNumber(setNumber);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (activeSetNumber === null) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Validate inputs
      if (setData.reps <= 0) {
        throw new Error('Reps must be greater than zero');
      }
      
      if (setData.weight < 0) {
        throw new Error('Weight cannot be negative');
      }
      
      if (setData.rpe !== undefined && (setData.rpe < 0 || setData.rpe > 10)) {
        throw new Error('RPE must be between 0 and 10');
      }

      // Only proceed if exerciseId is valid
      if (!validExerciseId) {
        throw new Error('Invalid exercise ID');
      }

      // Send data to API
      await trackExerciseSet(validExerciseId, activeSetNumber, {
        reps: setData.reps,
        weight: setData.weight,
        rpe: setData.rpe,
        completed: true,
        notes: setData.notes || undefined
      });

      // Close the set form
      setActiveSetNumber(null);
      
      // Notify parent component to refresh data
      if (typeof onSetTracked === 'function') {
        onSetTracked();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to log set');
      console.error('Error logging set:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Function to add a new set
  const addSet = () => {
    setActualSets(prev => prev + 1);
  };

  // Function to remove a set
  const removeSet = async (setNumber: number) => {
    // Don't allow removing the only set
    if (sets.length <= 1) {
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Check if this set exists in the backend (has been tracked)
      const existingSetData = setsDataMap[setNumber];
      
      if (existingSetData) {
        // If the set exists in the backend, call the delete API
        await deleteSet(validExerciseId, setNumber);
      }
      
      // Always decrement the set count
      setActualSets(prev => prev - 1);
      
      // If active set was removed, clear it
      if (activeSetNumber === setNumber) {
        setActiveSetNumber(null);
      }
      
      // Notify parent component to refresh data
      if (typeof onSetTracked === 'function') {
        onSetTracked();
      }
    } catch (err) {
      console.error('Error removing set:', err);
      setError('Failed to remove set. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate completion percentage for progress bar
  const completedSets = Object.values(setsDataMap).filter(set => set.completed).length;
  const completionPercentage = sets.length > 0 ? (completedSets / sets.length) * 100 : 0;

  return (
    <div className="mt-4">
      <h3 className="text-lg font-medium mb-3">Sets</h3>
      
      {/* Progress bar */}
      <div className="mb-4">
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className="bg-green-600 h-2.5 rounded-full" 
            style={{ width: `${completionPercentage}%` }}
          ></div>
        </div>
        <div className="mt-1 flex justify-between text-xs text-gray-500">
          <span>{completedSets} of {sets.length} sets completed</span>
          <span>{Math.round(completionPercentage)}%</span>
        </div>
      </div>
      
      {/* Set buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        {sets.map(setNumber => {
          const isCompleted = setsDataMap[setNumber]?.completed;
          const isActive = activeSetNumber === setNumber;
          
          return (
            <div key={setNumber} className="relative group">
              <button 
                onClick={() => selectSet(setNumber)}
                className={`w-12 h-12 rounded-full flex items-center justify-center font-medium ${
                  isCompleted
                    ? 'bg-green-100 text-green-800 border-2 border-green-300'
                    : isActive
                    ? 'bg-blue-100 text-blue-800 border-2 border-blue-500'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                {setNumber}
              </button>
              {/* Remove button - appears on hover */}
              {sets.length > 1 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeSet(setNumber);
                  }}
                  className="absolute -top-2 -right-2 bg-red-100 text-red-600 rounded-full p-1 hidden group-hover:block hover:bg-red-200"
                  title="Remove set"
                >
                  <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          );
        })}
        
        {/* Add set button */}
        <button
          onClick={addSet}
          className="w-12 h-12 rounded-full flex items-center justify-center font-medium bg-blue-50 text-blue-600 border-2 border-dashed border-blue-300 hover:bg-blue-100"
          title="Add set"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
      </div>
      
      {/* Set form */}
      {activeSetNumber !== null && (
        <form onSubmit={handleSubmit} className="border rounded-lg p-4 bg-gray-50 space-y-4">
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-medium text-gray-700">Set {activeSetNumber}</h4>
            {setsDataMap[activeSetNumber]?.completed && (
              <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">Completed</span>
            )}
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reps</label>
              <input
                type="number"
                name="reps"
                value={setData.reps}
                onChange={handleInputChange}
                className="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Weight</label>
              <input
                type="number"
                name="weight"
                value={setData.weight}
                onChange={handleInputChange}
                className="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="0"
                step="0.5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">RPE</label>
              <input
                type="number"
                name="rpe"
                value={setData.rpe || ''}
                onChange={handleInputChange}
                className="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="0-10"
                min="0"
                max="10"
                step="0.5"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              name="notes"
              value={setData.notes}
              onChange={handleInputChange}
              rows={2}
              className="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Optional notes about this set"
            />
          </div>
          
          <div className="flex justify-between">
            <FormButton
              type="button"
              variant="secondary"
              onClick={() => setActiveSetNumber(null)}
            >
              Cancel
            </FormButton>
            <FormButton
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
            >
              {setsDataMap[activeSetNumber]?.completed ? 'Update Set' : 'Complete Set'}
            </FormButton>
          </div>
        </form>
      )}
      
      {/* Sets summary when no active set */}
      {activeSetNumber === null && existingSetsData && existingSetsData.length > 0 && (
        <div className="mt-2">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Completed Sets</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Set</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reps</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weight</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RPE</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.values(setsDataMap)
                  .filter(setData => setData && typeof setData.set_number === 'number')
                  .sort((a, b) => (a.set_number || 0) - (b.set_number || 0))
                  .map(setData => (
                  <tr key={setData.set_number} 
                    className="hover:bg-gray-50 cursor-pointer" 
                    onClick={() => setData && typeof setData.set_number === 'number' && selectSet(setData.set_number)}
                  >
                    <td className="px-3 py-2 whitespace-nowrap text-sm">{setData.set_number}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm">{setData.reps}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm">{setData.weight}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm">{setData.rpe || '-'}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm">{setData.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {activeSetNumber === null && (!existingSetsData || existingSetsData.length === 0) && (
        <div className="text-center py-4 text-gray-500">
          <p className="mb-2">No sets tracked yet</p>
          <p className="text-sm">Click on a set number above to log your set data</p>
        </div>
      )}
      
      {/* Add set button at bottom */}
      {activeSetNumber === null && (
        <div className="mt-4 flex justify-center">
          <button
            onClick={addSet}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200"
          >
            <svg className="h-5 w-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Set
          </button>
        </div>
      )}
    </div>
  );
};

export default SetTracker;