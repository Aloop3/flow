import { useState, FormEvent } from 'react';

interface WeekFormProps {
  blockId: string;
  onSubmit: (weekData: any) => Promise<void>;
  isLoading: boolean;
  onCancel: () => void;
}

const WeekForm = ({ blockId, onSubmit, isLoading, onCancel }: WeekFormProps) => {
  const [formData, setFormData] = useState({
    block_id: blockId,
    week_number: 1,
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Form handlers and validation
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ 
      ...prev, 
      [name]: name === 'week_number' ? parseInt(value) || 0 : value 
    }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (formData.week_number <= 0) {
      newErrors.week_number = 'Week number must be positive';
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
      {/* Form fields */}
      <div>
        <label htmlFor="week_number" className="block text-sm font-medium text-gray-700">
          Week Number
        </label>
        <input
          type="number"
          id="week_number"
          name="week_number"
          min="1"
          value={formData.week_number}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            errors.week_number ? 'border-red-300' : ''
          }`}
        />
        {errors.week_number && <p className="mt-1 text-sm text-red-600">{errors.week_number}</p>}
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
          {isLoading ? 'Adding...' : 'Add Week'}
        </button>
      </div>
    </form>
  );
};

export default WeekForm;