import { useState } from 'react';
import { post } from 'aws-amplify/api';

interface Set {
  set_number: number;
  reps: number;
  weight: number;
  rpe?: number;
  notes?: string;
}

interface ExerciseFormProps {
  exerciseType: string;
  exerciseId: string;
  workoutId: string;
  onSetLogged: () => void;
}

export default function ExerciseForm({ exerciseType, exerciseId, workoutId, onSetLogged }: ExerciseFormProps) {
  const [sets, setSets] = useState<Set[]>([
    { set_number: 1, reps: 0, weight: 0 }
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addSet = () => {
    setSets([...sets, { set_number: sets.length + 1, reps: 0, weight: 0 }]);
  };

  const updateSet = (index: number, field: keyof Set, value: number | string) => {
    const updatedSets = [...sets];
    updatedSets[index] = { ...updatedSets[index], [field]: value };
    setSets(updatedSets);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Submit exercise with sets to API using the updated Amplify v6 syntax
      await post({
        apiName: 'flow-api',
        path: `/exercises/${exerciseId}/sets`,
        options: {
          body: {
            workout_id: workoutId,
            sets
          }
        }
      });
      onSetLogged();
    } catch (error) {
      console.error('Error logging exercise:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <h3 className="font-bold text-lg mb-4">{exerciseType}</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full min-w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Set</th>
              <th className="text-left py-2">Weight</th>
              <th className="text-left py-2">Reps</th>
              <th className="text-left py-2">RPE</th>
            </tr>
          </thead>
          <tbody>
            {sets.map((set, index) => (
              <tr key={index} className="border-b">
                <td className="py-2">{set.set_number}</td>
                <td className="py-2">
                  <input
                    type="number"
                    value={set.weight}
                    onChange={(e) => updateSet(index, 'weight', Number(e.target.value))}
                    className="w-20 p-1 border rounded"
                  />
                </td>
                <td className="py-2">
                  <input
                    type="number"
                    value={set.reps}
                    onChange={(e) => updateSet(index, 'reps', Number(e.target.value))}
                    className="w-16 p-1 border rounded"
                  />
                </td>
                <td className="py-2">
                  <input
                    type="number"
                    value={set.rpe || ''}
                    onChange={(e) => updateSet(index, 'rpe', Number(e.target.value))}
                    className="w-16 p-1 border rounded"
                    placeholder="1-10"
                    min="0"
                    max="10"
                    step="0.5"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 flex justify-between">
        <button
          onClick={addSet}
          className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >
          Add Set
        </button>
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {isSubmitting ? 'Saving...' : 'Save Exercise'}
        </button>
      </div>
    </div>
  );
}