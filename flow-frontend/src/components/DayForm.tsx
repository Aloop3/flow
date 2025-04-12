import { useState, FormEvent } from 'react';

interface DayFormProps {
  weekId: string;
  suggestedDayNumber: number;
  onSubmit: (dayData: any) => Promise<void>;
  isLoading: boolean;
  onCancel: () => void;
}

const DayForm = ({ weekId, suggestedDayNumber, onSubmit, isLoading, onCancel }: DayFormProps) => {
  const [formData, setFormData] = useState({
    week_id: weekId,
    day_number: suggestedDayNumber,
    date: new Date().toISOString().split('T')[0], // Current date in YYYY-MM-DD format
    focus: '',
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ 
      ...prev, 
      [name]: name === 'day_number' ? parseInt(value) || 0 : value 
    }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (formData.day_number <= 0) {
      newErrors.day_number = 'Day number must be positive';
    }
    
    if (!formData.date) {
      newErrors.date = 'Date is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="day_number" className="block text-sm font-medium text-gray-700">
          Day Number
        </label>
        <input
          type="number"
          id="day_number"
          name="day_number"
          min="1"
          value={formData.day_number}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            errors.day_number ? 'border-red-300' : ''
          }`}
        />
        {errors.day_number && <p className="mt-1 text-sm text-red-600">{errors.day_number}</p>}
      </div>
      
      <div>
        <label htmlFor="date" className="block text-sm font-medium text-gray-700">
          Date
        </label>
        <input
          type="date"
          id="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            errors.date ? 'border-red-300' : ''
          }`}
        />
        {errors.date && <p className="mt-1 text-sm text-red-600">{errors.date}</p>}
      </div>
      
      <div>
        <label htmlFor="focus" className="block text-sm font-medium text-gray-700">
          Focus
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
          {isLoading ? 'Adding...' : 'Add Day'}
        </button>
      </div>
    </form>
  );
};

export default DayForm;