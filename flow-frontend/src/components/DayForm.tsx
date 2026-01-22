import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import FocusTag from './FocusTag';
import { formatDate } from '../utils/dateUtils';

const dayFormSchema = z.object({
  day_id: z.string(),
  focus: z.string().optional(),
  notes: z.string().optional(),
});

type DayFormValues = z.infer<typeof dayFormSchema>;

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
  const form = useForm<DayFormValues>({
    resolver: zodResolver(dayFormSchema),
    defaultValues: {
      day_id: day.day_id,
      focus: day.focus || '',
      notes: day.notes || '',
    },
  });

  const focusOptions = [
    { value: 'squat', label: 'Squat' },
    { value: 'bench', label: 'Bench' },
    { value: 'deadlift', label: 'Deadlift' },
    { value: 'cardio', label: 'Cardio' },
    { value: 'rest', label: 'Rest' }
  ];

  const handleFormSubmit = async (data: DayFormValues) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Error updating day:', error);
    }
  };

  const selectedFocus = form.watch('focus');

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-4">
        <div className="mb-4">
          <h3 className="text-md font-medium text-gray-700">
            Day {day.day_number} - {formatDate(day.date)}
          </h3>
        </div>

        <FormField
          control={form.control}
          name="focus"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Training Focus</FormLabel>
              <FormControl>
                <div className="grid grid-cols-5 gap-2">
                  {focusOptions.map(option => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => field.onChange(option.value)}
                      className={`p-2 rounded border ${
                        field.value === option.value
                          ? 'ring-2 ring-blue-500 ring-offset-1'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <FocusTag focus={option.value} />
                    </button>
                  ))}
                </div>
              </FormControl>
              {selectedFocus && (
                <div className="mt-2">
                  <span className="text-sm text-muted-foreground">Selected: </span>
                  <FocusTag focus={selectedFocus} />
                </div>
              )}
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes</FormLabel>
              <FormControl>
                <Textarea
                  rows={3}
                  placeholder="Optional training notes for this day"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default DayForm;
