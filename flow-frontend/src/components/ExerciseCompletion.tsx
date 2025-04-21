import { useState } from 'react';
import FormButton from './FormButton';
import { completeExercise } from '../services/api';
import type { Exercise } from '../services/api';

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

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h3 className="text-lg font-medium">{exercise.exercise_type}</h3>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

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
  );
};

export default ExerciseCompletion;