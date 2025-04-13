import { useState, FormEvent, useEffect } from 'react';
import FormButton from './FormButton';

interface WeekFormProps {
  blockId: string;
  onSubmit: (weekData: any) => Promise<void>;
  isLoading: boolean;
  onCancel: () => void;
  initialData?: {
    week_number?: number;
    notes?: string;
  };
  existingWeekNumbers?: number[];
}

const WeekForm = ({ 
  blockId, 
  onSubmit, 
  isLoading, 
  onCancel,
  initialData = {},
  existingWeekNumbers = [] 
  }: WeekFormProps) => {
  const [formData, setFormData] = useState({
    block_id: blockId,
    week_number: initialData.week_number || 1,
    notes: initialData.notes || '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [suggestedWeekNumber, setSuggestedWeekNumber] = useState(1);

  // Find the next available week number on component mount
  useEffect(() => {
    if (existingWeekNumbers.length > 0) {
      const maxWeekNumber = Math.max(...existingWeekNumbers);
      setSuggestedWeekNumber(maxWeekNumber + 1);
      
      // Only set if we're not editing an existing week
      if (!initialData.week_number) {
        setFormData(prev => ({
          ...prev,
          week_number: maxWeekNumber + 1
        }));
      }
    }
  }, [existingWeekNumbers, initialData.week_number]);

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
    } else if (
      existingWeekNumbers.includes(formData.week_number) && 
      formData.week_number !== initialData.week_number
    ) {
      newErrors.week_number = 'Week number already exists in this program';
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
        {errors.week_number ? (
          <p className="mt-1 text-sm text-red-600">{errors.week_number}</p>
        ) : (
          <p className="mt-1 text-xs text-gray-500">
            Suggested: {suggestedWeekNumber} (next available number)
          </p>
        )}
      </div>
      
      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
          Notes <span className="text-xs text-gray-500">(optional)</span>
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
      
      <div className="flex justify-end space-x-3 pt-2">
        <FormButton
          type="button"
          onClick={onCancel}
          className="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          Cancel
        </FormButton>
        <FormButton
          type="submit"
          variant="primary"
          isLoading={isLoading}
          disabled={isLoading}
          className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400"
        >
          {initialData.week_number ? 'Update Week' : 'Add Week'}
        </FormButton>
      </div>
    </form>
  );
};

export default WeekForm;