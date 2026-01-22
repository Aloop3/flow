import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';

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
  // Create schema with custom validation for unique week numbers
  const weekFormSchema = z.object({
    block_id: z.string(),
    week_number: z.coerce.number().min(1, 'Week number must be positive').refine(
      (val) => !existingWeekNumbers.includes(val) || val === initialData.week_number,
      'Week number already exists in this program'
    ),
    notes: z.string().optional(),
  });

  type WeekFormValues = z.infer<typeof weekFormSchema>;

  // Calculate suggested week number
  const suggestedWeekNumber = existingWeekNumbers.length > 0
    ? Math.max(...existingWeekNumbers) + 1
    : 1;

  const form = useForm<WeekFormValues>({
    resolver: zodResolver(weekFormSchema),
    defaultValues: {
      block_id: blockId,
      week_number: initialData.week_number || suggestedWeekNumber,
      notes: initialData.notes || '',
    },
  });

  // Update week number when suggested changes (only for new weeks)
  useEffect(() => {
    if (!initialData.week_number && suggestedWeekNumber > 1) {
      form.setValue('week_number', suggestedWeekNumber);
    }
  }, [suggestedWeekNumber, initialData.week_number, form]);

  const handleFormSubmit = async (data: WeekFormValues) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="week_number"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Week Number</FormLabel>
              <FormControl>
                <Input type="number" min={1} {...field} />
              </FormControl>
              <FormDescription>
                Suggested: {suggestedWeekNumber} (next available number)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Notes <span className="text-xs text-muted-foreground">(optional)</span>
              </FormLabel>
              <FormControl>
                <Textarea rows={3} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end space-x-3 pt-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : initialData.week_number ? 'Update Week' : 'Add Week'}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default WeekForm;
