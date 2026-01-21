import { z } from 'zod';

export const setSchema = z.object({
  weight: z.number().min(0, 'Weight must be 0 or greater'),
  reps: z.number().min(1, 'Reps must be at least 1'),
  rpe: z.number().min(0).max(10).optional(),
  notes: z.string().optional(),
  completed: z.boolean(),
});

export type SetFormData = z.infer<typeof setSchema>;
