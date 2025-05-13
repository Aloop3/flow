import { useState, useEffect } from 'react';
import { trackExerciseSet, updateExercise, deleteSet, completeExercise } from '../services/api';
import type { Exercise, ExerciseSetData } from '../services/api';
import FormButton from './FormButton';

interface ExerciseTrackerProps {
  exercise: Exercise;
  onComplete: () => void;
  onCancel?: () => void;
  readOnly?: boolean;
}

const ExerciseTracker: React.FC<ExerciseTrackerProps> = ({ 
  exercise, 
  onComplete, 
  onCancel, 
  readOnly = false 
}) => {
  const [exerciseState, setExerciseState] = useState<Exercise>(exercise);
  const [activeSetNumber, setActiveSetNumber] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isReopening, setIsReopening] = useState(false);
  const [setData, setSetData] = useState({
    reps: exercise.reps || 0,
    weight: exercise.weight || 0,
    rpe: undefined as number | undefined,
    notes: '',
  });

  useEffect(() => {
    setExerciseState(exercise);
  }, [exercise]);

  const actualSets = Math.max(1, exerciseState.sets || 1);
  const sets = Array.from({ length: actualSets }, (_, i) => i + 1);

  const [allSetsCompleted, setAllSetsCompleted] = useState(false);
  const setsDataMap = (exerciseState.sets_data || []).reduce((map, setData) => {
    if (setData && typeof setData.set_number === 'number') {
      map[setData.set_number] = setData;
    }
    return map;
  }, {} as Record<number, ExerciseSetData>);

  const completedSets = Object.values(setsDataMap).filter(set => set.completed).length;
  const completionPercentage = sets.length > 0 ? (completedSets / sets.length) * 100 : 0;

  useEffect(() => {
    if (exerciseState.sets_data && exerciseState.sets_data.length > 0) {
      setAllSetsCompleted(completedSets >= exerciseState.sets);
    } else {
      setAllSetsCompleted(false);
    }
  }, [exerciseState.sets_data, exerciseState.sets, completedSets]);

  useEffect(() => {
    // If this is a completed exercise that we're now editing, automatically set it to in_progress
    if (exerciseState.status === 'completed' && !readOnly && !isReopening) {
      setIsReopening(true);
      
      // Automatically reopen the exercise when editing begins
      const reopenExercise = async () => {
        try {
          await updateExercise(exerciseState.exercise_id, {
            status: 'completed'
          });
          
          // Update local state first for responsive UI
          setExerciseState(prev => ({...prev, status: 'completed'}));
          
          // Then refresh from server
          onComplete();
        } catch (err) {
          console.error('Error reopening exercise:', err);
          // Continue anyway - let user edit locally even if API fails
        } finally {
          setIsReopening(false);
        }
      };
      
      reopenExercise();
    }
  }, [exerciseState.status, readOnly, exerciseState.exercise_id, onComplete, isReopening]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setSetData(prev => ({
      ...prev,
      [name]: name === 'notes' ? value : Number(value) || 0
    }));
  };

  const selectSet = (setNumber: number) => {
    if (readOnly) return;

    if (setsDataMap[setNumber]) {
      const existingData = setsDataMap[setNumber];
      setSetData({
        reps: existingData.reps || exerciseState.reps,
        weight: existingData.weight || exerciseState.weight,
        rpe: existingData.rpe,
        notes: existingData.notes || '',
      });
    } else {
      setSetData({
        reps: exerciseState.reps,
        weight: exerciseState.weight,
        rpe: undefined,
        notes: '',
      });
    }
    setActiveSetNumber(setNumber);
    setError(null);
  };

  const handleSubmitSet = async (e: React.FormEvent) => {
    e.preventDefault();
    if (activeSetNumber === null || readOnly) return;

    setIsSubmitting(true);
    setError(null);

    try {
      if (setData.reps <= 0) throw new Error('Reps must be greater than zero');
      if (setData.weight < 0) throw new Error('Weight cannot be negative');
      if (setData.rpe !== undefined && (setData.rpe < 0 || setData.rpe > 10)) {
        throw new Error('RPE must be between 0 and 10');
      }

      await trackExerciseSet(exerciseState.exercise_id, activeSetNumber, {
        reps: setData.reps,
        weight: setData.weight,
        rpe: setData.rpe,
        completed: true,
        notes: setData.notes || undefined
      });

      setActiveSetNumber(null);
      onComplete();
    } catch (err: any) {
      setError(err.message || 'Failed to log set');
      console.error('Error logging set:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addSet = async () => {
    if (readOnly) return;
    setIsSubmitting(true);
    setError(null);
  
    try {
      // Calculate new set count
      const newSetCount = exerciseState.sets + 1;
      
      // Update local state immediately for better UX
      setExerciseState(prev => ({ ...prev, sets: newSetCount }));
      
      // Instead of using updateExercise, create a "placeholder" set 
      // This implicitly creates the new set and updates the exercise
      await trackExerciseSet(exerciseState.exercise_id, newSetCount, {
        reps: exerciseState.reps,
        weight: exerciseState.weight,
        // Only include RPE if it exists
        ...(exerciseState.rpe !== undefined && { rpe: exerciseState.rpe }),
        completed: false  // Mark as not completed yet
      });
      
      // Refresh from server
      onComplete();
    } catch (err) {
      console.error('Error adding set:', err);
      // Revert local state on error
      setExerciseState(prev => ({ ...prev, sets: prev.sets - 1 }));
      setError('Failed to add set. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  

  const removeSet = async (setNumber: number) => {
    if (readOnly || sets.length <= 1) return;
    setIsSubmitting(true);
    setError(null);

    try {
      const existingSetData = setsDataMap[setNumber];
      if (existingSetData) {
        await deleteSet(exerciseState.exercise_id, setNumber);
      }

      if (activeSetNumber === setNumber) setActiveSetNumber(null);
      const currentActiveSet = activeSetNumber;
      onComplete();

      if (currentActiveSet && currentActiveSet !== setNumber) {
        setTimeout(() => setActiveSetNumber(currentActiveSet), 100);
      }
    } catch (err) {
      console.error('Error removing set:', err);
      setError('Failed to remove set. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCompleteExercise = async () => {
    if (readOnly) return;
    setIsSubmitting(true);
    setError(null);
  
    try {
      const trackedSets = exerciseState.sets_data?.filter(set => set.completed) || [];
      
      // Require at least one completed set
      if (trackedSets.length === 0) {
        setError('Please complete at least one set before marking the exercise as completed.');
        setIsSubmitting(false);
        return;
      }
  
      // Only use actually completed sets count
      const setCount = trackedSets.length;
      
      await completeExercise(exerciseState.exercise_id, {
        sets: setCount,
        reps: exerciseState.reps,
        weight: exerciseState.weight,
        rpe: exerciseState.rpe,
        notes: exerciseState.notes
        // Removed status field - let backend handle it
      });
      
      onComplete();
    } catch (err: any) {
      console.error('Error completing exercise:', err);
      setError(err.message || 'Failed to complete exercise');
    } finally {
      setIsSubmitting(false);
    }
  };

  const reopenExercise = async () => {
    if (readOnly) return;
    setIsSubmitting(true);
    setError(null);
  
    try {
      // Fix this to 'in_progress' instead of 'completed'
      await updateExercise(exerciseState.exercise_id, {
        status: 'planned'  // CHANGED FROM 'completed'
      });
      
      // Refresh data
      onComplete();
    } catch (err: any) {
      console.error('Error reopening exercise:', err);
      setError(err.message || 'Failed to reopen exercise');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      {/* Progress Bar */}
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
      
      {/* Set Buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        {sets.map(setNumber => {
          const isCompleted = setsDataMap[setNumber]?.completed;
          const isActive = activeSetNumber === setNumber;
          
          return (
            <div key={setNumber} className="relative group">
              <button 
                onClick={() => selectSet(setNumber)}
                disabled={readOnly}
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
              {!readOnly && sets.length > 1 && (
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
        {!readOnly && (
          <button
            onClick={addSet}
            className="w-12 h-12 rounded-full flex items-center justify-center font-medium bg-blue-50 text-blue-600 border-2 border-dashed border-blue-300 hover:bg-blue-100"
            title="Add set"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
        )}
      </div>
      
      {/* Set Form */}
      {activeSetNumber !== null && !readOnly && (
        <form onSubmit={handleSubmitSet} className="border rounded-lg p-4 bg-gray-50 space-y-4">
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-medium text-gray-700">Set {activeSetNumber}</h4>
            {setsDataMap[activeSetNumber]?.completed && (
              <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">Completed</span>
            )}
          </div>
          
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
      
      {/* Sets Table */}
      {activeSetNumber === null && exerciseState.sets_data && exerciseState.sets_data.length > 0 && (
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
                  <tr 
                    key={setData.set_number} 
                    className={`hover:bg-gray-50 ${!readOnly ? 'cursor-pointer' : ''}`}
                    onClick={() => !readOnly && setData && typeof setData.set_number === 'number' && selectSet(setData.set_number)}
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
      
      {/* Empty state message */}
      {activeSetNumber === null && (!exerciseState.sets_data || exerciseState.sets_data.length === 0) && (
        <div className="text-center py-4 text-gray-500">
          <p className="mb-2">No sets tracked yet</p>
          {!readOnly && (
            <p className="text-sm">Click on a set number above to log your set data</p>
          )}
        </div>
      )}
      
      {/* Action Buttons */}
        <div className="flex justify-between mt-4 pt-3 border-t">
        {/* Reopen button for completed exercises */}
        {exerciseState.status === 'completed' && !readOnly && activeSetNumber === null && (
            <FormButton 
            type="button" 
            variant="secondary"
            disabled={isSubmitting}
            isLoading={isSubmitting}
            onClick={reopenExercise}
            >
            Reopen Exercise
            </FormButton>
        )}

        {/* Show Complete button only for non-completed exercises */}
        {!readOnly && exerciseState.status !== 'completed' && exerciseState.sets_data && 
        exerciseState.sets_data.length > 0 && activeSetNumber === null && (
            <FormButton 
            type="button" 
            variant="primary"
            disabled={isSubmitting}
            isLoading={isSubmitting}
            onClick={handleCompleteExercise}
            >
            {allSetsCompleted ? "Update Exercise" : "Mark Exercise Complete"}
            </FormButton>
        )}
        
        {/* Add Set button - only visible for non-completed exercises */}
        {!readOnly && exerciseState.status !== 'completed' && activeSetNumber === null && (
            <button
            onClick={addSet}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200"
            >
            <svg className="h-5 w-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Set
            </button>
        )}
        
        {/* Cancel button */}
        {activeSetNumber === null && onCancel && (
            <FormButton 
            type="button" 
            variant="secondary" 
            onClick={onCancel}
            >
            Close
            </FormButton>
        )}
        </div>
    </div>
  );
}

export default ExerciseTracker;
