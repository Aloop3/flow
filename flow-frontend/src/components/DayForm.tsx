import { useState, FormEvent } from 'react';
import FocusTag from './FocusTag';
import { formatDate } from '../utils/dateUtils';

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
  
  const focusOptions = [
    { value: 'squat', label: 'Squat' },
    { value: 'bench', label: 'Bench' },
    { value: 'deadlift', label: 'Deadlift' },
    { value: 'cardio', label: 'Cardio' },
    { value: 'rest', label: 'Rest' }
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
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
        <h3 className="text-md font-medium text-gray-700">Day {day.day_number} - {formatDate(day.date)}</h3>
      </div>
      
      <div>
        <label htmlFor="focus" className="block text-sm font-medium text-gray-700 mb-2">
          Training Focus
        </label>
        <div className="grid grid-cols-5 gap-2 mb-3">
          {focusOptions.map(option => (
            <button
              key={option.value}
              type="button"
              onClick={() => setFormData(prev => ({ ...prev, focus: option.value }))}
              className={`p-2 rounded border ${
                formData.focus === option.value 
                  ? 'ring-2 ring-blue-500 ring-offset-1' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <FocusTag focus={option.value} />
            </button>
          ))}
        </div>
        {formData.focus && (
          <div className="mt-2">
            <span className="text-sm text-gray-500">Selected: </span>
            <FocusTag focus={formData.focus} />
          </div>
        )}
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