export const FOCUS_OPTIONS = [
  { value: 'squat', label: 'Squat' },
  { value: 'bench', label: 'Bench' },
  { value: 'deadlift', label: 'Deadlift' },
  { value: 'secondary_squat', label: 'Secondary Squat' },
  { value: 'secondary_bench', label: 'Secondary Bench' },
  { value: 'secondary_deadlift', label: 'Secondary Deadlift' },
  { value: 'sbd', label: 'SBD' },
  { value: 'rest', label: 'Rest' },
  { value: 'cardio', label: 'Cardio' },
] as const;

export type FocusValue = typeof FOCUS_OPTIONS[number]['value'];

export const MAX_FOCUS_SELECTIONS = 2;

export const parseFocusTags = (focus: string | null | undefined): string[] => {
  if (!focus) return [];
  return focus.split(',').map(f => f.trim().toLowerCase()).filter(Boolean);
};

export const formatFocusTags = (tags: string[]): string => {
  return tags.slice(0, MAX_FOCUS_SELECTIONS).join(',');
};
