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
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Block } from '../services/api';

const blockFormSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  status: z.enum(['draft', 'active', 'completed']),
  number_of_weeks: z.coerce.number().min(3, 'Minimum 3 weeks').max(12, 'Maximum 12 weeks'),
});

type BlockFormValues = z.infer<typeof blockFormSchema>;

interface BlockFormProps {
  initialData?: Partial<Block>;
  onSubmit: (blockData: Partial<Block>) => Promise<void>;
  isLoading: boolean;
}

const BlockForm = ({ initialData = {}, onSubmit, isLoading }: BlockFormProps) => {
  const form = useForm<BlockFormValues>({
    resolver: zodResolver(blockFormSchema),
    defaultValues: {
      title: initialData.title || '',
      description: initialData.description || '',
      start_date: initialData.start_date || '',
      end_date: initialData.end_date || '',
      status: initialData.status || 'draft',
      number_of_weeks: initialData.number_of_weeks || 4,
    },
  });

  const startDate = form.watch('start_date');
  const numberOfWeeks = form.watch('number_of_weeks');

  // Calculate end date when start date or number of weeks changes
  useEffect(() => {
    if (startDate && numberOfWeeks) {
      const start = new Date(startDate);
      const startDateUTC = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth(), start.getUTCDate(), 23, 59, 59));
      const endDate = new Date(startDateUTC);
      endDate.setUTCDate(startDateUTC.getUTCDate() + (numberOfWeeks * 7) - 1);
      const formattedEndDate = endDate.toISOString().split('T')[0];
      form.setValue('end_date', formattedEndDate);
      form.setValue('start_date', startDateUTC.toISOString().split('T')[0]);
    }
  }, [startDate, numberOfWeeks, form]);

  const handleFormSubmit = async (data: BlockFormValues) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea rows={3} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <FormField
            control={form.control}
            name="start_date"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Start Date</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="end_date"
            render={({ field }) => (
              <FormItem>
                <FormLabel>End Date</FormLabel>
                <FormControl>
                  <Input type="date" {...field} readOnly className="bg-muted" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="number_of_weeks"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Number of Weeks</FormLabel>
              <FormControl>
                <Input type="number" min={3} max={12} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default BlockForm;
