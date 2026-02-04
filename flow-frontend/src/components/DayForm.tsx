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
import { FOCUS_OPTIONS, MAX_FOCUS_SELECTIONS, parseFocusTags, formatFocusTags } from '../constants/focusOptions';

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

  const handleFormSubmit = async (data: DayFormValues) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Error updating day:', error);
    }
  };

  const selectedFocus = form.watch('focus');
  const selectedTags = parseFocusTags(selectedFocus);

  const handleTagToggle = (value: string, currentFocus: string) => {
    const tags = parseFocusTags(currentFocus);
    const index = tags.indexOf(value);

    if (index >= 0) {
      // Remove tag
      tags.splice(index, 1);
    } else if (tags.length < MAX_FOCUS_SELECTIONS) {
      // Add tag
      tags.push(value);
    }

    return formatFocusTags(tags);
  };

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
              <FormLabel>Training Focus (select up to {MAX_FOCUS_SELECTIONS})</FormLabel>
              <FormControl>
                <div className="grid grid-cols-3 gap-2">
                  {FOCUS_OPTIONS.map(option => {
                    const isSelected = selectedTags.includes(option.value);
                    const isDisabled = !isSelected && selectedTags.length >= MAX_FOCUS_SELECTIONS;
                    return (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => field.onChange(handleTagToggle(option.value, field.value || ''))}
                        disabled={isDisabled}
                        className={`p-2 rounded border transition-all ${
                          isSelected
                            ? 'ring-2 ring-ocean-teal ring-offset-1'
                            : isDisabled
                            ? 'border-gray-100 opacity-50 cursor-not-allowed'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <FocusTag focus={option.value} size="sm" />
                      </button>
                    );
                  })}
                </div>
              </FormControl>
              {selectedTags.length > 0 && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Selected:</span>
                  {selectedTags.map(tag => (
                    <FocusTag key={tag} focus={tag} size="sm" />
                  ))}
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
