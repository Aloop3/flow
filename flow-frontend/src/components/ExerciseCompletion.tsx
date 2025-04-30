import { useState, useEffect } from 'react';
import FormButton from './FormButton';
import { completeExercise } from '../services/api';
import type { Exercise } from '../services/api';
import SetTracker from './SetTracker';

interface ExerciseCompletionProps {
  exercise: Exercise;
  onComplete: () => void;
  onCancel: () => void;
}

const ExerciseCompletion = ({ exercise, onComplete, onCancel }: ExerciseCompletionProps) => {
  const [formData, setFormData] = useState({
    sets: exercise.sets,
    reps: exercise.reps,
    weight: exercise.weight,
    rpe: exercise.rpe || undefined,
    notes: exercise.notes || '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useSetTracker, setUseSetTracker] = useState(false);
  const [localExercise, setLocalExercise] = useState<Exercise>(exercise);

  // If the exercise already has sets_data, default to set tracker mode
  useEffect(() => {
    if (exercise.sets_data && exercise.sets_data.length > 0) {
      setUseSetTracker(true);
    }
  }, [exercise]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'notes' ? value : Number(value)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await completeExercise(exercise.exercise_id, formData);
      onComplete();
    } catch (err: any) {
      console.error('Error completing exercise:', err);
      setError(err.message || 'Failed to complete exercise');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSetTracked = () => {
    // Refresh the exercise state by notifying parent
    onComplete();
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">{exercise.exercise_type}</h3>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Toggle between modes */}
      <div className="flex justify-center border-b pb-3 mb-3">
        <div className="inline-flex rounded-md shadow-sm" role="group">
          <button
            type="button"
            onClick={() => setUseSetTracker(false)}
            className={`${
              !useSetTracker 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-50'
            } py-2 px-4 text-sm font-medium rounded-l-lg border border-gray-200`}
          >
            Complete All Sets
          </button>
          <button
            type="button"
            onClick={() => setUseSetTracker(true)}
            className={`${
              useSetTracker 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-50'
            } py-2 px-4 text-sm font-medium rounded-r-lg border border-gray-200`}
          >
            Track Individual Sets
          </button>
        </div>
      </div>

      {useSetTracker ? (
        <SetTracker 
          exerciseId={exercise.exercise_id}
          exerciseType={exercise.exercise_type}
          plannedSets={exercise.sets}
          plannedReps={exercise.reps}
          plannedWeight={exercise.weight}
          existingSetsData={exercise.sets_data}
          onSetTracked={handleSetTracked}
        />
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Sets</label>
              <input
                type="number"
                name="sets"
                value={formData.sets}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Reps</label>
              <input
                type="number"
                name="reps"
                value={formData.reps}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Weight</label>
              <input
                type="number"
                name="weight"
                value={formData.weight}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="0"
                step="0.5"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">RPE (optional)</label>
            <input
              type="number"
              name="rpe"
              value={formData.rpe || ''}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              min="0"
              max="10"
              step="0.5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Notes (optional)</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end space-x-3">
            <FormButton type="button" variant="secondary" onClick={onCancel}>
              Cancel
            </FormButton>
            <FormButton type="submit" variant="primary" isLoading={isLoading}>
              Complete Exercise
            </FormButton>
          </div>
        </form>
      )}

      <div className="flex justify-end mt-4">
        <FormButton type="button" variant="secondary" onClick={onCancel}>
          Close
        </FormButton>
      </div>
    </div>
  );
};

export default ExerciseCompletion;