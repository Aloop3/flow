import type { Exercise } from './api';

// Types
export interface SetData {
  weight: number;
  reps: number;
  rpe?: number;
  notes?: string;
  completed: boolean;
}

export interface WorkoutDraft {
  dayId: string;
  exercises: Exercise[];
  setsData: Record<string, Record<number, SetData>>; // exerciseId -> setNumber -> data
  lastModified: number;
  lastSynced: number;
  pendingChanges: PendingChange[];
}

export interface PendingChange {
  exerciseId: string;
  setNumber: number;
  data: Partial<SetData>;
  timestamp: number;
}

const STORAGE_KEY_PREFIX = 'workoutDraft_';

// Helper to get storage key
const getKey = (dayId: string) => `${STORAGE_KEY_PREFIX}${dayId}`;

export const workoutStorage = {
  /**
   * Load draft from localStorage, or initialize from server data
   */
  loadDraft(dayId: string, serverExercises?: Exercise[]): WorkoutDraft | null {
    const stored = localStorage.getItem(getKey(dayId));

    if (stored) {
      try {
        const draft = JSON.parse(stored) as WorkoutDraft;
        return draft;
      } catch {
        localStorage.removeItem(getKey(dayId));
      }
    }

    // No draft exists, initialize from server data
    if (serverExercises && serverExercises.length > 0) {
      return this.initializeDraft(dayId, serverExercises);
    }

    return null;
  },

  /**
   * Initialize a new draft from server exercise data
   */
  initializeDraft(dayId: string, exercises: Exercise[]): WorkoutDraft {
    const setsData: Record<string, Record<number, SetData>> = {};

    exercises.forEach(exercise => {
      setsData[exercise.exercise_id] = {};

      // Initialize from existing sets_data if available
      (exercise.sets_data || []).forEach(setData => {
        setsData[exercise.exercise_id][setData.set_number] = {
          weight: setData.weight,
          reps: setData.reps,
          rpe: setData.rpe,
          notes: setData.notes,
          completed: setData.completed || false,
        };
      });

      // Fill in missing sets with planned values
      for (let i = 1; i <= exercise.sets; i++) {
        if (!setsData[exercise.exercise_id][i]) {
          setsData[exercise.exercise_id][i] = {
            weight: exercise.weight,
            reps: exercise.reps,
            rpe: exercise.rpe,
            completed: false,
          };
        }
      }
    });

    const draft: WorkoutDraft = {
      dayId,
      exercises,
      setsData,
      lastModified: Date.now(),
      lastSynced: Date.now(),
      pendingChanges: [],
    };

    this.saveDraft(draft);
    return draft;
  },

  /**
   * Save draft to localStorage
   */
  saveDraft(draft: WorkoutDraft): void {
    draft.lastModified = Date.now();
    localStorage.setItem(getKey(draft.dayId), JSON.stringify(draft));
  },

  /**
   * Update a specific set's data
   */
  updateSet(dayId: string, exerciseId: string, setNumber: number, data: Partial<SetData>): void {
    const draft = this.loadDraft(dayId);
    if (!draft) return;

    // Ensure exercise exists in setsData
    if (!draft.setsData[exerciseId]) {
      draft.setsData[exerciseId] = {};
    }

    // Merge with existing data
    draft.setsData[exerciseId][setNumber] = {
      ...draft.setsData[exerciseId][setNumber],
      ...data,
    };

    // Add to pending changes queue
    draft.pendingChanges.push({
      exerciseId,
      setNumber,
      data,
      timestamp: Date.now(),
    });

    this.saveDraft(draft);
  },

  /**
   * Toggle completion status for a set
   */
  toggleSetCompletion(dayId: string, exerciseId: string, setNumber: number): boolean {
    const draft = this.loadDraft(dayId);
    if (!draft) return false;

    // Ensure exercise and set exist
    if (!draft.setsData[exerciseId]) {
      draft.setsData[exerciseId] = {};
    }
    if (!draft.setsData[exerciseId][setNumber]) {
      // Initialize with defaults if set doesn't exist
      const exercise = draft.exercises.find(e => e.exercise_id === exerciseId);
      draft.setsData[exerciseId][setNumber] = {
        weight: exercise?.weight || 0,
        reps: exercise?.reps || 0,
        rpe: exercise?.rpe,
        completed: false,
      };
    }

    // Toggle completion
    const newCompleted = !draft.setsData[exerciseId][setNumber].completed;
    draft.setsData[exerciseId][setNumber].completed = newCompleted;

    // Add to pending changes queue
    draft.pendingChanges.push({
      exerciseId,
      setNumber,
      data: { completed: newCompleted },
      timestamp: Date.now(),
    });

    this.saveDraft(draft);
    return newCompleted;
  },

  /**
   * Remove a set from the draft (used when deleting a set)
   * When removing the last set, simply delete it. When removing a middle set, renumber.
   */
  removeSet(dayId: string, exerciseId: string, setNumber: number): void {
    const draft = this.loadDraft(dayId);
    if (!draft || !draft.setsData[exerciseId]) return;

    // Get current sets and find the highest set number
    const sets = draft.setsData[exerciseId];
    const setNumbers = Object.keys(sets).map(Number).sort((a, b) => a - b);

    if (setNumbers.length === 0) return;

    // Remove the specified set and any sets with higher numbers
    // This handles the "remove last set" case cleanly
    for (const num of setNumbers) {
      if (num >= setNumber) {
        delete sets[num];
      }
    }

    this.saveDraft(draft);
  },

  /**
   * Get data for a specific set
   */
  getSet(dayId: string, exerciseId: string, setNumber: number): SetData | undefined {
    const draft = this.loadDraft(dayId);
    return draft?.setsData[exerciseId]?.[setNumber];
  },

  /**
   * Get all sets for an exercise
   */
  getExerciseSets(dayId: string, exerciseId: string): Record<number, SetData> {
    const draft = this.loadDraft(dayId);
    return draft?.setsData[exerciseId] || {};
  },

  /**
   * Get completion stats for an exercise
   */
  getExerciseCompletion(dayId: string, exerciseId: string, totalSets: number): { completed: number; total: number } {
    const sets = this.getExerciseSets(dayId, exerciseId);
    const completed = Object.values(sets).filter(s => s?.completed).length;
    return { completed, total: totalSets };
  },

  /**
   * Clear draft after workout completion
   */
  clearDraft(dayId: string): void {
    localStorage.removeItem(getKey(dayId));
  },

  /**
   * Check if a draft exists (for resume workout feature)
   */
  hasDraft(dayId: string): boolean {
    return localStorage.getItem(getKey(dayId)) !== null;
  },

  /**
   * Get pending changes and clear the queue
   */
  consumePendingChanges(dayId: string): PendingChange[] {
    const draft = this.loadDraft(dayId);
    if (!draft) return [];

    const changes = [...draft.pendingChanges];
    draft.pendingChanges = [];
    this.saveDraft(draft);

    return changes;
  },

  /**
   * Mark sync as complete
   */
  markSynced(dayId: string): void {
    const draft = this.loadDraft(dayId);
    if (!draft) return;

    draft.lastSynced = Date.now();
    this.saveDraft(draft);
  },

  /**
   * Get all draft day IDs (for finding unfinished workouts)
   */
  getAllDraftIds(): string[] {
    const ids: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(STORAGE_KEY_PREFIX)) {
        ids.push(key.replace(STORAGE_KEY_PREFIX, ''));
      }
    }
    return ids;
  },
};
