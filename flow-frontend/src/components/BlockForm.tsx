import { useState, FormEvent, useEffect } from 'react';
import { Block } from '../services/api';

interface BlockFormProps {
  initialData?: Partial<Block>;
  onSubmit: (blockData: Partial<Block>) => Promise<void>;
  isLoading: boolean;
}

const BlockForm = ({ initialData = {}, onSubmit, isLoading }: BlockFormProps) => {
  const [formData, setFormData] = useState({
    title: initialData.title || '',
    description: initialData.description || '',
    start_date: initialData.start_date || '',
    end_date: initialData.end_date || '',
    status: initialData.status || 'draft',
    number_of_weeks: initialData.number_of_weeks || 4,
  });
  useEffect(() => {
    if (formData.start_date && formData.number_of_weeks) {
      // Create a new Date object from start date
      const startDate = new Date(formData.start_date);
      // Get the UTC version of the start date
      const startDateUTC = new Date(Date.UTC(startDate.getUTCFullYear(), startDate.getUTCMonth(), startDate.getUTCDate(), 23, 59, 59));
      console.log("Start date (UTC):", startDateUTC.toISOString());
      // Calculate end date: start date + (number_of_weeks * 7) days
      const endDate = new Date(startDateUTC);
      console.log('Initial end date (UTC):', endDate.toISOString());
      endDate.setUTCDate(startDateUTC.getUTCDate() + (formData.number_of_weeks * 7) - 1);
      
      // Format as YYYY-MM-DD
      const formattedEndDate = endDate.toISOString().split('T')[0];
      setFormData(prev => ({
        ...prev,
        start_date: startDateUTC.toISOString().split('T')[0],
        end_date: formattedEndDate
      }));
      console.log('Updated end date (UTC):', formattedEndDate);
    }
  }, [formData.start_date, formData.number_of_weeks]);

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (formData.number_of_weeks < 4 || formData.number_of_weeks > 12) {
      newErrors.number_of_weeks = 'Number of weeks must be between 4 and 12';
    }

    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required';
    }
    
    if (!formData.end_date) {
      newErrors.end_date = 'End date is required';
    } else if (formData.start_date && new Date(formData.end_date) <= new Date(formData.start_date)) {
      newErrors.end_date = 'End date must be after start date';
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
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Form fields */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            errors.title ? 'border-red-300' : ''
          }`}
        />
        {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
      </div>
      
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          rows={3}
          value={formData.description}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">
            Start Date
          </label>
          <input
            type="date"
            id="start_date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              errors.start_date ? 'border-red-300' : ''
            }`}
          />
          {errors.start_date && <p className="mt-1 text-sm text-red-600">{errors.start_date}</p>}
        </div>
        
        <div>
          <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">
            End Date
          </label>
          <input
            type="date"
            id="end_date"
            name="end_date"
            value={formData.end_date}
            readOnly
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.end_date && <p className="mt-1 text-sm text-red-600">{errors.end_date}</p>}
        </div>
      </div>
      
      <div>
        <label htmlFor="number_of_weeks" className="block text-sm font-medium text-gray-700">
          Number of Weeks
        </label>
        <input
          type="number"
          id="number_of_weeks"
          name="number_of_weeks"
          min="4"
          max="12"
          value={formData.number_of_weeks}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            errors.number_of_weeks ? 'border-red-300' : ''
          }`}
        />
        {errors.number_of_weeks && <p className="mt-1 text-sm text-red-600">{errors.number_of_weeks}</p>}
      </div>

      <div>
        <label htmlFor="status" className="block text-sm font-medium text-gray-700">
          Status
        </label>
        <select
          id="status"
          name="status"
          value={formData.status}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
        </select>
      </div>
      
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400"
        >
          {isLoading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  );
};

export default BlockForm;