import { useState, FormEvent } from 'react';

interface DayFormProps {
  day: {
    day_id: string;
    day_number: number;
    date: string;
    focus?: string;
    notes?: string;
  };
  onSubmit: (dayData: any) => Promise<void>;
  isLoading: boolean;
  onCancel: () => void;
}

const DayForm = ({ day, onSubmit, isLoading, onCancel }: DayFormProps) => {
  const [formData, setFormData] = useState({
    day_id: day.day_id,
    focus: day.focus || '',
    notes: day.notes || '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Error updating day:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="mb-4">
        <h3 className="text-md font-medium text-gray-700">Day {day.day_number} - {new Date(day.date).toLocaleDateString()}</h3>
      </div>
      
      <div>
        <label htmlFor="focus" className="block text-sm font-medium text-gray-700">
          Training Focus
        </label>
        <select
          id="focus"
          name="focus"
          value={formData.focus}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Select a focus (optional)</option>
          <option value="squat">Squat</option>
          <option value="bench">Bench</option>
          <option value="deadlift">Deadlift</option>
          <option value="cardio">Cardio</option>
          <option value="rest">Rest</option>
        </select>
      </div>
      
      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
          Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows={3}
          value={formData.notes}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="Optional training notes for this day"
        />
      </div>
      
      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400"
        >
          {isLoading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
};

export default DayForm;